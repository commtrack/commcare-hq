from django.conf.urls.defaults import *

urlpatterns = patterns('',
#    (r'^calender$', 'calender.views.google'),
    (r'^calender$', 'aquatest_calendar.views.view'),
    (r'^sample_popup$', 'aquatest_calendar.views.sample_popup'),
#    (r'^calenderjs$', 'calender.views.countdaysamples'),

)

