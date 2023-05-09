import csv
from django.contrib.gis.geos import Point
from .models import VehicleType, Depot, Vehicle

def load_vehicle_types():
    with open('../data/vehicules_urgence_localisation.csv', 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            VehicleType.objects.create(name=row['nom'])

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
            vehicle_type = VehicleType.objects.get(name=row['nom'])
            depot = Depot.objects.get(location=Point(float(row['vehicule_lng']), float(row['vehicule_lat'])))
            Vehicle.objects.create(vehicle_type=vehicle_type, depot=depot, capacity=int(row['capacite']))

def load_data():
    load_vehicle_types()
    load_depots()
    load_vehicles()
