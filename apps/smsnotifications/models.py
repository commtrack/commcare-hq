from datetime import datetime
import httplib, urllib
from threading import Thread

from django.db import models
from django.db.models.signals import post_save

from samples.models import *
from reporters.models import Reporter
from wqm.models import SamplingPoint, WqmArea, WqmAuthority
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

def send_sms_notifications(sub, vals, form_xmlns):
    # TODO: Lookup the reporters based on the sample point and
    # figure out who to send to, what to send
    
    form = FormDefModel.objects.get(target_namespace = form_xmlns)
    choice = NotificationChoice.objects.get(xform = form)
    print '---------------->>>>>>>>>>>  %s  <<<<<<<<<<<------------'% (choice,)
        
    reporter = sub.taken_by
    point = sub.sampling_point
    # A temporary SMS Response
    # TODO: Auto generate response SMS. to the sample sender (tester)
    msg = "Aquatest: Your sample data is submitted sucessfully.!"
    # sending an sms.
    thread = Thread(target=_send_sms,args=(reporter.id, msg ))
    thread.start()

    # create massage for the authorised testers in the Notification table
    # sample sms: Test taken at site Borehole - Brandvlei. H2S positive Comment: Am out of chlorine
    msg2 = "Test taken at site %s - %s." % (point.wqmarea, point)
    print '----------- %s -----------------'% (msg2,)
    # query all the notification to the submitted point. for that xform
    notices = SmsNotification.objects.filter(sampling_point=point,notification_type=choice)
    print '----------- %s -----------------'% (notices,)
    for notice in notices:
        print '----------- %s -----------------'% (notice,)
        reporter = notice.authorised_sampler
        #check if failure notification
        if notice.failure_notification:
            print 'A: Failure Notification----------- %s -----------------'% (notice.failure_notification,)
            above = 'above range'
            below = 'below range'
            msg3 = ''
            msg3 += 'Their is an abnormal range in the sample'
            thread = Thread(target=_send_sms,args=(reporter.id, msg3 ))
            thread.start()
            
            for value in vals:
                print '################ %s #############' % (value,)
                # unexpected result when working with abnormal range.
#                if abnormal_range(value):
#                    print 'A: Range----------- %s -----------------'% ('True',)
#                else:
#                    print 'Range----------- %s -----------------'% ('False',)
        else:
            print 'B: Failure Notification----------- %s -----------------'% (notice.failure_notification,)
            msg4 = ''
            for value in vals:
                msg4 =msg2 + " %s:%s" % (value.parameter.test_name, value.value)
            msg4 += '. Comment: %s'%(sub.notes)
            thread = Thread(target=_send_sms,args=(reporter.id, msg4 ))
            thread.start()
        
    
    
    

