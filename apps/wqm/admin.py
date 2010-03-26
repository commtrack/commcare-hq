from wqm.models import WqmAuthority,WqmArea,SamplingPoint
from django.contrib import admin
from hq.models import *
from resources.models import *
from django.contrib import admin



class WqmAuthorityAdmin(admin.ModelAdmin):
    list_display = ('name', 'modified', 'created')
    search_fields = ('name', 'modified', 'created')
    list_filter = ['name']
admin.site.register(WqmAuthority, WqmAuthorityAdmin)

class WqmAreaAdmin(admin.ModelAdmin):
    list_display = ('name', 'wqmauthority', 'modified', 'created')
    search_fields = ('name', 'wqmauthority', 'modified', 'created')
    list_filter = ['name']
admin.site.register(WqmArea, WqmAreaAdmin)

class SamplingPointAdmin(admin.ModelAdmin):
    list_display = ('name', 'wqmarea', 'modified', 'created')
    search_fields = ('name', 'wqmarea', 'modified', 'created')
    list_filter = ['name']
admin.site.register(SamplingPoint, SamplingPointAdmin)

