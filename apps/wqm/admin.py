#from django.contrib import admin
from django.contrib.gis import admin
#from django.contrib.gis.maps.google import GoogleMap

#GMAP = GoogleMap(key='abcdefg') # Can also set GOOGLE_MAPS_API_KEY in settings

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
#    fieldsets = (
#        (None, {
#            'fields' : ('name', 'modified', 'created')
#        }),
#    )
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

#class SamplingPointAdmin(admin.ModelAdmin):
#    list_display = ('name', 'wqmarea', 'modified', 'created')
#    search_fields = ('name', 'wqmarea', 'modified', 'created')
#    list_filter = ['name']
#    fieldsets = (
#        (None, {
#            'fields' : ('name', 'code', 'wqmarea', 'modified', 'created')
#        }),
#        ('Coordinates', {
#            'fields' : ('latitude', 'longitude')
#        })
#    )
#admin.site.register(SamplingPoint, SamplingPointAdmin)
admin.site.register(SamplingPoint, admin.GeoModelAdmin)

admin.site.register(DelivarySystem)
