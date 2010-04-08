from datetime import datetime
import httplib, urllib
from threading import Thread

from django.db import models
from django.db.models.signals import post_save

from samples.models import Sample
from reporters.models import Reporter
from wqm.models import SamplingPoint
from xformmanager.models import FormDefModel

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

#def _add_choice(sender, instance, created, **kwargs): #get sender, instance, created
#    # TODO: add a domain filter.
#    if not created:     return
#    print '<<<<<<<<<<<<<<<<<< ADDING CHOICE >>>>>>>>>>>>>>>>>>>>>'
#    xchoice = NotificationChoice()
#    try:
#        print '<<<<<<<<<<<<<<<<<< TRY 1 >>>>>>>>>>>>>>>>>>>>>'
#        xchoice.choice = instance.form_display_name
#        print '<<<<<<<<<<<<<<<<<< TRY 2 >>>>>>>>>>>>>>>>>>>>>'
#        xchoice.xform = instance
#        print '<<<<<<<<<<<<<<<<<< TRY 3 >>>>>>>>>>>>>>>>>>>>>'
#    except Exception, e:
#        # TODO: report error.
#        print '<<<<<<<<<<<<<<<<<< error >>>>>>>>>>>>>>>>>>>>>'
#        raise
#    xchoice.save()
#    print '<<<<<<<<<<<<<<<<<< TRY 4 >>>>>>>>>>>>>>>>>>>>>'

class SmsNotification(models.Model):
    sampling_point = models.ForeignKey(SamplingPoint)
    authorised_sampler = models.ForeignKey(Reporter)
    # notification_type = models.CharField(max_length=160, choices=NOTIFICATION_TYPE_CHOICES)
    # TODO: Notification shuld be selected from the type of xforms.
    notification_type = models.ForeignKey(NotificationChoice)
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
    point = instance.sampling_point

    # A temporary SMS Response
    # TODO: Auto generate response SMS.
    msg = "Aquatest: Sample data have been submitted."
    # sending an sms to a submitter.
    thread = Thread(target=_send_sms,args=(reporter.id, msg ))
    thread.start()

    # figure out who to send sms to in the notifation table.
    notices = SmsNotification.objects.filter(sampling_point = point)
    for notice in notices:
        reporter = notice.authorised_sampler
        # TODO: generate a sms according the the authorised tester.
        # this is temp sms to authorised sampler
        msg = "Aquatest: Sample is submited from %s %s " % (instance.sampling_point.wqmarea, instance.sampling_point )
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

# register to receive signals each time an xform is saved.
# TODO: add signal on delete too.
#post_save.connect(_add_choice, sender=FormDefModel)