from django.forms import ModelForm
from smsnotifications.models import SmsNotification
from wqm.models import WqmAuthority, WqmArea, SamplingPoint

class SmsNotificationForm(ModelForm):
    class Meta:
        model = SmsNotification
        exclude = ('modified','created',)