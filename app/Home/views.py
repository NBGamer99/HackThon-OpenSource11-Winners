from django.shortcuts import render
from datetime import datetime
from .models import Incident, VehicleType, Vehicle
from .utils import load_data
from django.contrib.gis.geos import Point

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


        coordinates, inc_type, lvl = format_data(inc_type, lvl, lat, lng)

    # Fin desired vehicule
    qualif_vehicule = wish_vehicules(inc_type, VEHICULE)
    valid_vehicule = validate_vehicule(lvl, qualif_vehicule)

    better_one = wish_one_suit_better(coordinates, valid_vehicule)

    start_coordination = (better_one['vehicule_lat'], better_one['vehicule_lng'])

    # generate the map
    rd_map = get_the_map(start_coordination, coordinates)
    html_map = rd_map._repr_html_()

    cont = {
        "vehicule": better_one,
        "map": html_map,
        "from" : get_address_from_latlng(start_coordination),
        "to" : get_address_from_latlng(coordinates),
        "time": datetime.now(),
        "incident": tmp,
        "degree" : "High" if lvl == 3 else "Low" if lvl == 1 else "Medium",
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

def format_data(type, lvl, lat, lng):
    coordinates = (lat, lng)
    inc_type = Type.CRIME if type == "CRIME" else Type.INJURY if type == "INJURY" else Type.FIRE
    lvl = check_and_factorize(lvl)
    if not isinstance(lvl, int):
        raise ("We need multiple requests to manage this!")
    return coordinates, inc_type, lvl

def wish_vehicules(inc_type, df):
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

def wish_one_suit_better(coordinates, valid_vehicules):

    # Define the point of interest
    poi_lat = coordinates[0]
    poi_lon = coordinates[1]

    # Calculate the distance from each point to the point of interest
    valid_vehicules['distance'] = valid_vehicules.apply(lambda row: haversine(row['vehicule_lat'], row['vehicule_lng'], poi_lat, poi_lon), axis=1)

    better_one = valid_vehicules.nsmallest(1, 'distance')

    return better_one.to_dict(orient='records')[0]


# ------------- Find the optimal path and draw the map ------------------
import osmnx as ox
import networkx as nx
from geopy.geocoders import Nominatim
import folium as fl

ox.settings.log_console=True
ox.settings.use_cache=True

def get_the_map(start_coordination, end_coordination):
    locator = Nominatim(user_agent = "Khouribga Map")
    place     = 'Khouribga, Morocco'# find shortest route based on the mode of travel
    mode      = 'drive'
    optimizer = 'length'

    graph = ox.graph_from_place(place, network_type = mode)

    orig_node = ox.distance.nearest_nodes(graph, start_coordination[1],
                                      start_coordination[0])# find the nearest node to the end location
    dest_node = ox.distance.nearest_nodes(graph, end_coordination[1],
                                      end_coordination[0])

    shortest_route = nx.shortest_path(graph,
                                  orig_node,
                                  dest_node,
                                  weight=optimizer)

    shortest_route_map = ox.plot_route_folium(graph, shortest_route,
                                          tiles='openstreetmap')
    fl.Marker(start_coordination, icon=fl.Icon(color="red", icon="star", prefix="fa")).add_to(shortest_route_map)
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