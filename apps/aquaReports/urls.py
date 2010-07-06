from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^index', 'aquaReports.views.index'),
    (r'^aquareports$', 'aquaReports.views.samplesreport_index'),
    (r'^aquareports/testers$', 'aquaReports.views.samplesreport_testers'),
    (r'^aquareports/parameters$', 'aquaReports.views.samplesreport_parameters'),
#    (r'^samplereport$', 'aquaReports.views.samplesreport'),
#    (r'^pdfview','aquaReports.views.pdf_view'),
#    (r'^report_testers','aquaReports.views.report_testers'),
)


