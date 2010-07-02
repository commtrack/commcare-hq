from datetime import datetime
import httplib, urllib
from threading import Thread

#from samples.models import AbnormalRange # already in samples.models.py 

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
    print "---------------You TEXTING -----------------------"
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
            msg3 = msg2
            msg3 += 'Their is an abnormal range in the sample'
            thread = Thread(target=_send_sms,args=(reporter.id, msg3 ))
            thread.start()

            
            for value in vals:
                print '################ %s #############' % (value,)
                # check if values is abnomal and append to msg3
#                if abnormal_range(value):
#                    test_name, test_value = abnormal_range(value)
#                    msg3 += "%s:%s, " % (test_name, test_value)
#                if abnormal_range(value):
#                    print 'A: Range----------- %s -----------------'% ('True',)
#                else:
#                    print 'Range----------- %s -----------------'% ('False',)
                # check if no abnormal values found dnt send a sms
        else:
            print 'B: No failures Notification----------- %s -----------------'% (notice.failure_notification,)
            msg4 = msg2
            for value in vals:
                msg4 += " %s:%s, " % (value.parameter.test_name_short, value.value)
            msg4 += '. Comment: %s'%(sub.notes)
            thread = Thread(target=_send_sms,args=(reporter.id, msg4 ))
            thread.start()