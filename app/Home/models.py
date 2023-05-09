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
    incident_type = models.CharField(max_length=20)


class VehicleType(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self):
        return self.name


class Vehicle(models.Model):
    id = models.BigAutoField(primary_key=True)
    vehicle_type = models.ForeignKey(VehicleType, on_delete=models.CASCADE)
    depot = models.ForeignKey('Depot', on_delete=models.CASCADE)
    #TODO validate capacity 1 - 3
    capacity = models.PositiveIntegerField()



class Depot(models.Model):
    id = models.BigAutoField(primary_key=True)
    location = models.PointField(default=None)

    def __str__(self):
        return str(self.id)