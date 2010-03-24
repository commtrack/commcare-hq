from datetime import datetime
import httplib, urllib
from threading import Thread

from django.db import models
from django.db.models.signals import post_save

from samples.models import Sample
from reporters.models import Reporter
from wqm.models import SamplingPoint


class SmsNotification(models.Model):
    sampling_point = models.ForeignKey(SamplingPoint)
    authorised_sampler = models.ForeignKey(Reporter)
    notification_type = models.CharField(max_length=50)
    digest = models.BooleanField()
    modified = models.DateTimeField(null=True, blank=True)
    created = models.DateTimeField(default=datetime.now())


def __unicode__(self):
        return self.notification_type

def send_sms_notifications(sender, instance, created, **kwargs): #get sender, instance, created
    # TODO: Lookup the reporters based on the sample point and 
    # figure out who to send to, what to send
    # print sender.notes
    reporter = instance.taken_by
    msg = "A test message from AquaTest!"
    # msg = str(instance.notes)
    thread = Thread(target=_send_sms,args=(reporter.id, msg ))
    thread.start()

def _send_sms(reporter_id, message_text):     
    data = {"uid":  reporter_id,
            "text": message_text
            }
    encoded = urllib.urlencode(data)
    headers = {"Content-type": "application/x-www-form-urlencoded",
               "Accept": "text/plain"}
    try:
        conn = httplib.HTTPConnection("localhost:8000") # TODO: DON'T HARD CODE THIS!
        conn.request("POST", "/ajax/messaging/send_message", encoded, headers)
        response = conn.getresponse()
    except Exception, e:
        # TODO: better error reporting
        raise


# Register to receive signals each time a Sample is saved
post_save.connect(send_sms_notifications, sender=Sample)