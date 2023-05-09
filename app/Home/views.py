from django.shortcuts import render
from datetime import datetime
from .models import Incident, Vehicle
from .utils import load_data
from django.contrib.gis.geos import Point
from math import radians, cos, sin, asin, sqrt
import googlemaps


# Create your views here.

def home(request):
    if Vehicle.objects.first() is None:
        load_data()
    return render(request, 'index.html')

def sendHelp(request):
    if request.method == 'POST':
        levels = ['High', 'Medium', 'Low']
        inc_type = request.POST.get('type')
        lvl = int(request.POST.get('lvl'))
        desc = request.POST.get('description')


        # nvm ghire 3gezt 9ado
        tmp = inc_type

        lat = float(request.POST.get('lat'))
        lng = float(request.POST.get('lng'))

        inc_obj = Incident.objects.create(description=desc, location=Point(lng,lat), level=levels[lvl-1], incident_type=inc_type)


        coordinates, inc_type, lvl = format_data(inc_obj.id, lvl, lat, lng)

    # Fin desired vehicule
    qualif_vehicule = which_vehicules(inc_type, VEHICULE)
    valid_vehicule = validate_vehicule(lvl, qualif_vehicule)

    better_one = which_one_suits_better(coordinates, valid_vehicule)

    start_coordination = (better_one['vehicule_lat'], better_one['vehicule_lng'])

    # generate the map
    rd_map = get_the_map(start_coordination, coordinates, tmp)
    html_map = rd_map._repr_html_()

    turns = get_turns_number(start_coordination,(lat, lng))

    cont = {
        "vehicule": better_one,
        "map": html_map,
        "from" : get_address_from_latlng(start_coordination),
        "to" : get_address_from_latlng(coordinates),
        "time": datetime.now(),
        "incident": tmp,
        "degree" : "High" if lvl == 3 else "Low" if lvl == 1 else "Medium",
        "turns" : turns,
    }

    return render(request, 'sendHelp.html', cont)





# ------------------------------  Helper Functions ----------------------------------
import pandas as pd
from enum import Enum
import numpy as np

#-------------- CONSTANTS ------------------------
VEHICULE = pd.read_csv("../data/vehicules_urgence_localisation.csv")
SITE = pd.read_csv("../data/sites_incidents.csv")



def get_stations_location(df):
    locations = [(x,y) for x,y in zip(df['vehicule_lat'], df['vehicule_lng'])]
    return locations

def get_site_location(df, index):
    site = dict(df.iloc[index])
    location = (site['site_lat'], site['site_lng'])
    return location

class Type(Enum):
    FIRE = 1
    CRIME = 2
    INJURY = 3

def check_and_factorize(n):
    if n > 3:
        factors = []
        for i in [3, 2, 1]:
            while n >= i:
                factors.append(i)
                n -= i
        return factors
    else:
        return n

# def format_data(type, lvl, lat, lng):
#     coordinates = (lat, lng)
#     inc_type = Type.CRIME if type == "CRIME" else Type.INJURY if type == "INJURY" else Type.FIRE
#     lvl = check_and_factorize(lvl)
#     if not isinstance(lvl, int):
#         raise ("We need multiple requests to manage this!")
#     return coordinates, inc_type, lvl

def format_data(id, lvl, lat, lng):
    coordinates = (lat, lng)
    inc_type = Incident.objects.get(id=id).incident_type
    lvl = check_and_factorize(lvl)
    if not isinstance(lvl, int):
        raise ValueError("We need multiple requests to manage this!")
    return coordinates, inc_type, lvl

def which_vehicules(inc_type, df):
    if inc_type == Type.FIRE :
        return df[df['vehicule_type'] == 1]
    elif inc_type == Type.CRIME :
        return df[df['vehicule_type'] == 2 ]
    else :
        return df[df['vehicule_type'] == 3]

def validate_vehicule(lvl, df):
    valid_vehicule = df[df['capacite'] >= lvl]
    return valid_vehicule

# ---------- find wish one suit better ----------

# Define the Haversine formula to calculate the distance between two points
def haversine(lat1, lon1, lat2, lon2):
    r = 6371  # Earth's radius in kilometers
    dlat = np.radians(lat2 - lat1)
    dlon = np.radians(lon2 - lon1)
    a = np.sin(dlat/2)**2 + np.cos(np.radians(lat1)) * np.cos(np.radians(lat2)) * np.sin(dlon/2)**2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))
    distance = r * c
    return distance

def which_one_suits_better(coordinates, valid_vehicules):

    # Define the point of interest
    poi_lat, poi_lon = coordinates

    # Calculate the distance from each point to the point of interest
    valid_vehicules['distance'] = valid_vehicules.apply(lambda row: haversine(row['vehicule_lat'], row['vehicule_lng'], poi_lat, poi_lon), axis=1)

    better_one = valid_vehicules.nsmallest(1, 'distance')

    return better_one.to_dict(orient='records')[0]



# ------------- Find the optimal path and draw the map ------------------
import osmnx as ox
import networkx as nx
from geopy.geocoders import Nominatim
import folium as fl
import json

ox.settings.log_console=True
ox.settings.use_cache=True
def get_turns_number(origin, destination):
    # replace YOUR_API_KEY with your actual API key
    gmaps = googlemaps.Client(key='AIzaSyA7WTj7mP7fG9oZ1SnkzVKtQ1KXadqurJU')

    # get the directions from Google Maps
    directions = gmaps.directions(origin, destination)

    # count the number of turns
    num_turns = 0
    for step in directions[0]['legs'][0]['steps']:
        if 'maneuver' in step:
            num_turns += 1
    save_file = open("../data/data.json", "w")
    json.dump(directions, save_file, indent = 6)
    print(json.dump(directions, save_file, indent = 6))
    save_file.close()
    return num_turns

def get_the_map(start_coordination, end_coordination, type):
    icons = {'CRIME':'star', 'FIRE':'fire-extinguisher', 'INJURY':'star-of-life'}
    colors = {'CRIME':'blue', 'FIRE':'red', 'INJURY':'pink'}
    locator = Nominatim(user_agent = "Khouribga Map")
    place     = 'Khouribga, Morocco'# find shortest route based on the mode of travel
    mode      = 'drive'
    optimizer = 'turns'

    graph = ox.graph_from_place(place, network_type = mode)

    orig_node = ox.distance.nearest_nodes(graph, start_coordination[1],
                                      start_coordination[0])# find the nearest node to the end location
    dest_node = ox.distance.nearest_nodes(graph, end_coordination[1],
                                      end_coordination[0])

    def dist(a, b):
        (lat1 , lon1 )= a
        (lat2,  lon2 ) = b
        R = 6372.8  # Earth radius in kilometers
        dLat = radians(lat2 - lat1)
        dLon = radians(lon2 - lon1)
        lat1 = radians(lat1)
        lat2 = radians(lat2)
        a = sin(dLat/2)**2 + cos(lat1)*cos(lat2)*sin(dLon/2)**2
        c = 2*asin(sqrt(a))
        return R*c

    def heuristic(node, goal):
        # Calculate the straight-line distance between the node and the goal
        node_data = graph.nodes[node]
        goal_data = graph.nodes[goal]
        node_coords = (node_data['y'], node_data['x'])
        goal_coords = (goal_data['y'], goal_data['x'])
        distance = dist(node_coords, goal_coords)

        # Calculate the number of turns between the current node and the goal
        path = nx.shortest_path(graph, node, goal, weight='length')
        turns = sum(1 for i in range(1, len(path)-1) if graph.nodes.get(path[i], {}).get('lanes'))

        return distance + turns



    shortest_route = nx.astar_path(graph,
                                  orig_node,
                                  dest_node,
                                  heuristic=heuristic,
                                  weight=optimizer,
                                  )

    shortest_route_map = ox.plot_route_folium(graph, shortest_route,tiles='openstreetmap')
    fl.Marker(start_coordination, icon=fl.Icon(color=colors[type], icon=icons[type], prefix="fa")).add_to(shortest_route_map)
    fl.Marker(end_coordination, icon=fl.Icon(color="orange", icon="triangle-exclamation", prefix="fa")).add_to(shortest_route_map)
    return shortest_route_map


def get_address_from_latlng(coordination):
    # Initialize a geolocator with Nominatim
    geolocator = Nominatim(user_agent='myapp')

    # Get the location object from the latitude and longitude
    location = geolocator.reverse(coordination, exactly_one=True)

    # Get the address string from the location object
    address = location.address

    return address.split(',', 1)[0]