#from standards.models import Standard,WaterUseType
from django.contrib import admin
#from hq.models import *
from aquatest_calendar.models import *
from django.contrib import admin

'''
customize
'''

class EventAdmin(admin.ModelAdmin):
    list_display = ('name', 'desc','when','cal')
    search_fields = ('name', 'desc','when','cal')
    list_filter = ['name', 'desc','when','cal']
admin.site.register(Event, EventAdmin)

class EventCalendarAdmin(admin.ModelAdmin):
    list_display = ('owner','year','month')
    search_fields = ('owner','year','month')
    list_filter = ['owner','year','month']
admin.site.register(EventCalendar, EventCalendarAdmin)

