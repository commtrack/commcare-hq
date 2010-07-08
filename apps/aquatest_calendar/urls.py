from django.conf.urls.defaults import *

from djangoEventCal.cal.controller import CalendarController
from djangoEventCal.cal.models import Event

## calendar view
urlpatterns = patterns('aquatest_calendar.views',
#    (r'^calendernew$', 'view'),
    (r'^calender$', 'view'),
    (r'^samplepopup/?$', 'samples_popup'),
#    (r'^view/.*$', 'view'),
    (r'^upd/.*$', 'updEvent'),
    (r'^calenderadd/.*$', 'addEvent'),
    (r'^del/.*$', 'delEvent'),
#    (r'^.*$', 'view'),
)


#
#urlpatterns = patterns('',
##    (r'^calendernew$', 'aquatest_calendar.views.new'),
#    (r'^calender$', 'aquatest_calendar.views.view'),
#    (r'^calenderadd$', 'aquatest_calendar.views.addEvent'),
#    (r'^sample_popup$', 'aquatest_calendar.views.sample_popup'),
##    (r'^calenderjs$', 'calender.views.countdaysamples'),
#
#)

