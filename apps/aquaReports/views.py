import logging
import hashlib
import settings
import traceback
import sys
import os
import uuid
import string
from datetime import timedelta
from graphing import dbhelper
from reportlab.pdfgen import canvas
from django.http import HttpResponse
from django.http import HttpResponseRedirect, Http404
from django.template import RequestContext
from django.core.exceptions import *
from django.views.decorators.http import require_http_methods
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _
from django.db import transaction
from django.db.models.query_utils import Q
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import redirect_to_login
from django.contrib.auth.forms import AdminPasswordChangeForm
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType

from rapidsms.webui.utils import render_to_response, paginated

from xformmanager.models import *
from hq.models import *
from graphing.models import *
from receiver.models import *

from domain.decorators import login_and_domain_required

from reporters.models import Reporter

from wqm.models import SamplingPoint, WqmAuthority, WqmArea
from samples.models import Parameter, Sample, MeasuredValue

logger_set = False

def message(req, msg, link=None):
    return render_to_response(req,
        "message.html", {
            "message": msg,
            "link": link
    })

@login_and_domain_required
def index(req):
    return render_to_response(req,
        "samplesreport.html")

def get_tester(current_user):
    # todo: get the testers in the system with the same
    # domain as the login user.
    rep_profile = ReporterProfile.objects.filter(domain=current_user.selected_domain)
    reporters = []

    if rep_profile:
        for rep in rep_profile:
            reporter = rep.reporter
            reporters.append(reporter)
    return reporters

def samplesreport(req):
    points = SamplingPoint.objects.all()
    testers = get_tester(req.user)
    parameters = Parameter.objects.all()
    return render_to_response(req,
        "samplesreport.html", {
        "points": points,
        #"testers": testers,
        #"parameters" : parameters,
    })

def report_testers(req):
#    points = req.POST.get("points","")
#    selected_point = SamplingPoint.objects.filter(id = points)
#    samples = Sample.objects.filter(sampling_point=selected_point)
#    return render_to_response(req, 'samplesreport.html', {'testers' : samples})
    choice1 = req.POST.get("points","")
    choice2 = req.POST.get("testers","")
    choice3 = req.POST.get("parameters","")
    para = None
    samples = None
#    reports = None
    if choice1:
        selected_point = SamplingPoint.objects.filter(id = choice1)
        samples = Sample.objects.filter(sampling_point=selected_point)

    else:
        choice1 = req.POST.get('sel_points','')

    if choice2:
        para = Parameter.objects.all()
    else:
        choice2 = req.POST.get('sel_testers','')
        
    if choice3:
#        reports = 'This is the report.'
        selected_point = SamplingPoint.objects.filter(id = choice1)
        sel_repo = Reporter.objects.filter(id = choice2)
        sel_para = Parameter.objects.filter(id = choice3)
        reports = MeasuredValue.objects.filter( sample__sampling_point=selected_point,
                                                sample__taken_by=sel_repo,
                                                parameter=sel_para)
    else:
        reports = None
        
    return render_to_response(req, 'samplesreport.html',{   'parameters'    : para,
                                                            'testers'       : samples,
                                                            'sel_points'    : choice1,
                                                            'sel_testers'   : choice2,
                                                            'reports'        : reports,
                                                        })




def comma(string_or_list):
    """ TODO - this could probably go in some sort of global util file """
    if isinstance(string_or_list, basestring):
        string = string_or_list
        return string
    else:
        list = string_or_list
        return ", ".join(list)

def pdf_view(request):
    # Create the HttpResponse object with the appropriate PDF headers.
    response = HttpResponse(mimetype='application/pdf')
    #    this is for makin pdf as an attachent file
    #    response['Content-Disposition'] = 'attachment; filename=hello.pdf'
    response['Content-Disposition'] = 'filename=hello.pdf'
    p = canvas.Canvas(response)
    # Create the PDF object, using the response object as its "file."

    # Draw things on the PDF. Here's where the PDF generation happens.
    # See the ReportLab documentation for the full list of functionality.
    p.drawString(100, 100, "AquaTest Report!!!....on PDF!")

    p.showPage()
    p.save()
    return response

def date_range(req):
    pass

def wqm_ares(req):
    """
    from wqm.models import SamplingPoint
    """
    ares = SamplingPoint.objects.all()
    return ares

def sample_points(req):
    """
    from samples.models import Sample
    """
    samples = Sample.objects.filter()
    return samples