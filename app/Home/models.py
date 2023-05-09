# from django.db import models
from django.contrib.gis.db import models


# Create your models here.

class Incident(models.Model):
    id = models.AutoField(primary_key=True)
    HIGH = 'High'
    MEDIUM = 'Medium'
    LOW = 'Low'
    INCIDENT_LEVEL_CHOICES = [
        (HIGH, 'High'),
        (MEDIUM, 'Medium'),
        (LOW, 'Low'),
    ]

    description = models.TextField()
    location = models.PointField()
    level = models.CharField(max_length=10, choices=INCIDENT_LEVEL_CHOICES)
    incident_type = models.CharField(max_length=20)

class Vehicle(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=30)
    vehicle_type = models.CharField(max_length=10)
    depot = models.ForeignKey('Depot', on_delete=models.CASCADE)
    #TODO validate capacity 1 - 3
    capacity = models.PositiveIntegerField()



class Depot(models.Model):
    id = models.BigAutoField(primary_key=True)
    location = models.PointField(default=None)


    def __str__(self):
        return str(self.id)



class Route(models.Model):
    id = models.BigAutoField(primary_key=True)
    chemin = models.CharField(max_length=20)
    distance = models.CharField(max_length=20)
    vehicule_id = models.ForeignKey('Vehicle', on_delete=models.CASCADE)
    turns = models.CharField(max_length=20)

