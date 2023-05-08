# from django.db import models
from django.contrib.gis.db import models

# Create your models here.

class Incident(models.Model):
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
    incident_type = models.ForeignKey('VehicleType', on_delete=models.CASCADE)


class VehicleType(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self):
        return self.name


class Vehicle(models.Model):
    vehicle_type = models.ForeignKey(VehicleType, on_delete=models.CASCADE)
    depot = models.ForeignKey('Depot', on_delete=models.CASCADE)
    capacity = models.IntegerField()


class Depot(models.Model):
    name = models.CharField(max_length=100)
    location = models.PointField()

    def __str__(self):
        return self.name