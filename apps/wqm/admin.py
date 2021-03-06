#from django.contrib import admin
from django.contrib.gis import admin
from django.contrib.gis.maps.google import GoogleMap

GMAP = GoogleMap(key='ABQIAAAAwLx05eiFcJGGICFj_Nm3yxSy7OMGWhZNIeCBzFBsFwAAIleLbBRLVT87XVW-AJJ4ZR3UOs3-8BnQ-A') # Can also set GOOGLE_MAPS_API_KEY in settings

from hq.models import *
from wqm.models import WqmAuthority, WqmArea, SamplingPoint, DelivarySystem

#admin.site.register(WqmAuthority, admin.GeoModelAdmin)
#
#class GoogleAdmin(admin.OSMGeoAdmin):
#    extra_js = [GMAP.api_url + GMAP.key]
#    map_template = 'wqm/admin/google.html'
#
#admin.site.register(WqmAuthority, GoogleAdmin)
#admin.site.register(WorldBorders, admin.OSMGeoAd

class WqmAuthorityAdmin(admin.ModelAdmin):
    list_display = ('name', 'modified', 'created')
    search_fields = ('name', 'modified', 'created')
    list_filter = ['name']
    fieldsets = (
        (None, {
            'fields' : ('name', 'modified', 'created')
        }),
    )
admin.site.register(WqmAuthority, WqmAuthorityAdmin)

class WqmAreaAdmin(admin.ModelAdmin):
    list_display = ('name', 'wqmauthority', 'modified', 'created')
    search_fields = ('name', 'wqmauthority', 'modified', 'created')
    list_filter = ['name']
    fieldsets = (
        (None, {
            'fields' : ('name', 'wqmauthority', 'modified', 'created')
        }),
    )
admin.site.register(WqmArea, WqmAreaAdmin)

class SamplingPointAdmin(admin.OSMGeoAdmin):
    list_display = ('name', 'wqmarea', 'modified', 'created')
    search_fields = ('name', 'wqmarea', 'modified', 'created')
    list_filter = ['name']
    fieldsets = (
        (None, {
            'fields' : ('name', 'code', 'wqmarea', 'modified', 'created')
        }),
        (None, {
            'fields' : ('point_type', 'delivary_system','treatement')
        }),
        ('Map', {
            'fields' : ('point',)
        }),
    )
admin.site.register(SamplingPoint, SamplingPointAdmin)
#admin.site.register(SamplingPoint, admin.GeoModelAdmin)


admin.site.register(DelivarySystem)

class SamplingPointAdminGoogle(admin.OSMGeoAdmin):
    extra_js = [GMAP.api_url + GMAP.key]
    map_template = 'wqm/admin/google.html'
    
    list_display = ('name', 'wqmarea', 'modified', 'created')
    search_fields = ('name', 'wqmarea', 'modified', 'created')
    list_filter = ['name']
    fieldsets = (
        (None, {
            'fields' : ('name', 'code', 'wqmarea', 'modified', 'created')
        }),
        (None, {
            'fields' : ('point_type', 'delivary_system','treatement')
        }),
        ('Map', {
            'fields' : ('point',)
        }),
    )
# Register the google enabled admin site
google_admin = admin.AdminSite()
google_admin.register(SamplingPoint, SamplingPointAdminGoogle)

