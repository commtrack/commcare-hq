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

#from wqm.models import SamplingPoint, WqmAuthority, WqmArea
from samples.models import Parameter, Sample, MeasuredValue
from aquaReports.forms import SelectSamplingPointForm, SelectParameterForm, SelectTesterForm

logger_set = False

points_list = []        # selected sampling_points
testers_list = []       # selected testers
parameters_list = []    # selected parameters 

def message(req, msg, link=None):
    return render_to_response(req,
        "message.html", {
            "message": msg,
            "link": link
    })

@login_and_domain_required
def index(req):
    selected_point = points_list[0]
    selected_reporters = testers_list[0]
    selected_parameters = parameters_list[0]
    
    points_list.pop()
    testers_list.pop()
    parameters_list.pop()
    
    reports = MeasuredValue.objects.filter( sample__sampling_point__in = selected_point,
                                            parameter__in = selected_parameters)
    reports = reports.filter(sample__taken_by__in = selected_reporters)
    return render_to_response(req,
        "aquareports.html", {
        "reports": reports,
        "samplingpoints" :selected_point,
        "testers": selected_reporters,
        "parameters": selected_parameters, 
    })

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


@login_and_domain_required
def samplesreport_index(request):
    if request.method == 'POST': # If the form has been submitted...
        form = SelectSamplingPointForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            sl_points = form.cleaned_data['sampling_points']
            points_list.append(sl_points)
            url = '/aquareports/testers'
            return HttpResponseRedirect(url) # Redirect after POST
    else:
        form = SelectSamplingPointForm() # An unbound form

    return render_to_response(request,
        "samplesreport.html", {
        "form": form,
    })

def samplesreport_testers(request):
    ss = points_list[0]
    if request.method == 'POST': # If the form has been submitted...
        form = SelectTesterForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            sl_testers = form.cleaned_data['testers']
            testers_list.append(sl_testers)
            url = '/aquareports/parameters'
            return HttpResponseRedirect(url) # Redirect after POST
    else:
        form = SelectTesterForm() # An unbound form

    return render_to_response(request,
        "samplesreport.html", {
        "form": form,
    })


def samplesreport_parameters(request):
    ss = testers_list[0]
    if request.method == 'POST': # If the form has been submitted...
        form = SelectParameterForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            sl_parameters = form.cleaned_data['parameters']
            parameters_list.append(sl_parameters)
            url = '/index'
            return HttpResponseRedirect(url)
    else:
        form = SelectParameterForm() # An unbound form

    return render_to_response(request,
        "samplesreport.html", {
        "form": form,
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
    #    this is for making PDF as an attachment file
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
