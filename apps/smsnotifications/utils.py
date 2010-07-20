from datetime import datetime
from datetime import datetime
import httplib, urllib
from threading import Thread
from xformmanager.models import FormDefModel

from smsnotifications.models import NotificationChoice, SmsNotification

def _send_sms(reporter_id, message_text):
    print '~~~~~~~~~~~~~~~ IN _SEND_SMS ~~~~~~~~~~~~~~~'
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
    print "---------------You TEXTING -----------------------"
    form = FormDefModel.objects.get(target_namespace = form_xmlns)
    n_choice = NotificationChoice.objects.get(xform = form)
    print '---------------->>>>>>>>>>>  %s  <<<<<<<<<<<------------'% (n_choice,)
    
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
    notices = SmsNotification.objects.filter(sampling_point=point,notification_type=n_choice)
    print '----------- %s -----------------'% (notices,)
    
    for notice in notices:
        print '----------- %s -----------------'% (notice,)
        reporter = notice.authorised_sampler
        #check if failure notification
        if notice.failure_notification:
            print 'A: Yes Failure Notification----------- %s -----------------'% (notice.failure_notification,)
              
            msg3 = msg2
            ab_present = False # notifies if their is an abnormal range found
            
            for value in vals:
                if value.is_abnormal:
                    ab_present = True
                    print '^^^^^^^^^^^^^ %s ^^^^^^^^^^^^^^^' % (value,)
                    msg3 += "%s:%s, " % (value.parameter.test_name_short, value.value)
                else:
                    print "just a value ```````````````"
            # check if abnormal values found and send a sms
            if ab_present:
                thread = Thread(target=_send_sms,args=(reporter.id, msg3 ))
                thread.start()
        else:
            print 'B: No failures Notification----------- %s -----------------'% (notice.failure_notification,)
            msg4 = msg2
            for value in vals:
                msg4 += " %s:%s, " % (value.parameter.test_name_short, value.value)
            msg4 += '. Comment: %s'%(sub.notes)
            thread = Thread(target=_send_sms,args=(reporter.id, msg4 ))
            thread.start()

#def abnormal_range(value):
#    """
#        Check if the value in the MeasuredValue is within abnormal range
#        and returns True to within range and False where-else
#    """
#    ab_range = AbnormalRange.objects.get(value_rule__parameter = value__parameter)
#    min = ab_range.minimum
#    max = ab_range.maximum
#    if value.value in range(min,max):
#        return "True"
#    else:
#        return "False"
