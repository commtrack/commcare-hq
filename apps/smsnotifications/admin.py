from smsnotifications.models import SmsNotification
from django.contrib import admin
from hq.models import *

class SmsNotificationAdmin(admin.ModelAdmin):
    list_display = ('sampling_point', 'authorised_sampler', 'notification_type','digest','modified','created')
    search_fields = ('sampling_point', 'authorised_sampler', 'notification_type','digest','modified','created')
    list_filter = ['sampling_point', 'authorised_sampler', 'notification_type']
admin.site.register(SmsNotification,SmsNotificationAdmin)


