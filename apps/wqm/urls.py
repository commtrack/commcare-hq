from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^samplingpoints$', 'wqm.views.samplingpoints'),
    (r'^samplingpoints/(?P<pk>\d+)$', 'wqm.views.samplingpoints_edit'),
    (r'^samplingpoints/add$', 'wqm.views.samplingpoints_add'),
)