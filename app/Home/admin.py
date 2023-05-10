from django.contrib import admin
from .models import Incident, Vehicle, Depot
# Register your models here.

class IncidentAdminConfig(admin.ModelAdmin):
	list_display = ( 'description', 'location','level', 'incident_type')

class VehicleAdminConfig(admin.ModelAdmin):
	list_display = ('id', 'name', 'depot', 'capacity', 'vehicle_type')

class DepotAdminConfig(admin.ModelAdmin):
	list_display = ('id','location')
class RouteAdminConfig(admin.ModelAdmin):
	list_display = ('id','chemin', 'distance', 'vehicule_id', 'turns')

admin.site.register(Incident, IncidentAdminConfig)
admin.site.register(Vehicle, VehicleAdminConfig)
admin.site.register(Depot, DepotAdminConfig)
