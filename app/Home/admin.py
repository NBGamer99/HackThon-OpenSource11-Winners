from django.contrib import admin
from .models import Incident, Vehicle, Depot, VehicleType
# Register your models here.

class IncidentAdminConfig(admin.ModelAdmin):
	list_display = ( 'description', 'location','level', 'incident_type')

class VehicleAdminConfig(admin.ModelAdmin):
	list_display = ('id', 'vehicle_type', 'depot', 'capacity')

class VehicleTypeAdminConfig(admin.ModelAdmin):
	list_display = ('name',)

class DepotAdminConfig(admin.ModelAdmin):
	list_display = ('id','location')

admin.site.register(Incident, IncidentAdminConfig)
admin.site.register(Vehicle, VehicleAdminConfig)
admin.site.register(Depot, DepotAdminConfig)
admin.site.register(VehicleType, VehicleTypeAdminConfig)
