from datetime import datetime

from django.db import models
#from django.db.models.signals import post_save
from xformmanager.models import FormDefModel

from reporters.models import Reporter
from wqm.models import SamplingPoint

# TODO: auto-create a notication choices as the xform is added to a domain.
# link the notification type to the xform
#NOTIFICATION_TYPE_CHOICES = (
#    (u'all', u'All'),
#    (u'http://www.aquatest-za.org/h2s', u'h2s'),
#    (u'http://www.aquatest-za.org/physchem', u'physchem'),
#)

class NotificationChoice(models.Model):
    choice = models.CharField(max_length=255)
    xform = models.ForeignKey(FormDefModel)

    def __unicode__(self):
        return self.choice

class SmsNotification(models.Model):
    sampling_point = models.ManyToManyField(SamplingPoint)
    authorised_sampler = models.ForeignKey(Reporter)
    # TODO: Notification should be selected from the type of xforms.
    notification_type = models.ForeignKey(NotificationChoice)
    failure_notification = models.BooleanField(default=False, help_text="select if you want to send sms only when value is out of range")
    digest = models.BooleanField(default=False)
    modified = models.DateTimeField(null=True, blank=True)
    created = models.DateTimeField(default=datetime.now())
    
    def __unicode__(self):
            return '%s notification for %s'%(self.notification_type, self.authorised_sampler)
