from django.contrib import admin
from calender.models import SyncEvent



class SyncEventAdmin(admin.ModelAdmin):
    list_display = ('event_id','date','status')
    search_fields = ('event_id','date','status')
    list_filter = ['event_id','date','status']
admin.site.register(SyncEvent, SyncEventAdmin)