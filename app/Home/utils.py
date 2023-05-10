import csv
from django.contrib.gis.geos import Point
from .models import Depot, Vehicle

def load_depots():
    depots = {}
    with open('../data/vehicules_urgence_localisation.csv', 'r') as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            lat = float(row['vehicule_lat'])
            lng = float(row['vehicule_lng'])
            if (lat, lng) not in depots:
                depot = Depot.objects.create(id=i+1,location=Point(lng, lat))
                depots[(lat, lng)] = depot

def load_vehicles():
    with open('../data/vehicules_urgence_localisation.csv', 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            lat = float(row['vehicule_lat'])
            lng = float(row['vehicule_lng'])
            # vehicle_type = Vehicle.objects.get(vehicle_type=row['vehicule_type'])
            depot = Depot.objects.get(location=Point(lng, lat))
            Vehicle.objects.create(name=row['nom'] ,vehicle_type=row['vehicule_type'], depot=depot, capacity=int(row['capacite']))

def load_data():
    load_depots()
    load_vehicles()
