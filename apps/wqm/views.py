import logging
import hashlib
import settings
import traceback
import sys
import os
import uuid
import string
from datetime import timedelta
import datetime
from graphing import dbhelper

from django.template.loader import render_to_string
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

import hq.utils as utils
import hq.reporter as reporter
import hq.reporter.custom as custom
import hq.reporter.metastats as metastats

import hq.reporter.inspector as repinspector
import hq.reporter.metadata as metadata
from domain.decorators import login_and_domain_required

from reporters.utils import *
from reporters.views import message, check_reporter_form, update_reporter
#from reporters.models import Reporter, PersistantBackend, PersistantConnection
from reporters.models import *
from wqm.models import SamplingPoint, WqmAuthority, WqmArea, DelivarySystem
#from wqm.forms import SamplingPointForm, DateForm
from samples.models import Sample, AbnormalRange, MeasuredValue, ValueRule
from reporters.utils import *
from wqm.forms import DateForm, SamplingPointForm

def message(req, msg, link=None):
    return render_to_response(req,
        "message.html", {
            "message": msg,
            "link": link
    })

@login_and_domain_required
def index(req):
    columns = (("name", "Point Name"),
               ("wqmarea", "Area"),
               )
    sort_column, sort_descending = _get_sort_info(req, default_sort_column="name",
                                                  default_sort_descending=False)
    sort_desc_string = "-" if sort_descending else ""
    search_string = req.REQUEST.get("q", "")

    query = SamplingPoint.objects.order_by("%s%s" % (sort_desc_string, sort_column))

    if search_string == "":
        query = query.all()

    else:
        district = WqmAuthority.objects.get(id = search_string)
        query = query.filter(
           Q(wqmarea__wqmauthority__id=district.id ))
        search_string = district
    
    points = paginated(req, query)
    return render_to_response(req,
        "index.html", {
                       "columns": columns,
                       "points": points, 
                       "districts": WqmAuthority.objects.all(),
                       "sort_column": sort_column,
                       "sort_descending": sort_descending,
                       "search_string": search_string,
    })

def _get_sort_info(request, default_sort_column, default_sort_descending):
    sort_column = default_sort_column
    sort_descending = default_sort_descending
    if "sort_column" in request.GET:
        sort_column = request.GET["sort_column"]
    if "sort_descending" in request.GET:
        if request.GET["sort_descending"].startswith("f"):
            sort_descending = False
        else:
            sort_descending = True
    return (sort_column, sort_descending)

@login_and_domain_required
def edit_samplingpoints(request, pk):
    template_name = "samplingpoints.html"
    point = get_object_or_404(SamplingPoint, pk=pk)
    if request.method == 'POST': # If the form has been submitted...
        form = SamplingPointForm(request.POST, instance = point) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            # saving the form data is not cleaned
            form.save()
            return message(request,
                        "SMS Notification Updated",
                        link="/samplingpoints")
    else:
        form = SamplingPointForm(instance = point) # An unbound form

    return render_to_response(request,template_name, {
        'form': form,
        'point': point
    })

def check_point_form(req):

    # verify that all non-blank
    # fields were provided
#    missing = [
#        field.verbose_name
#        for field in SamplingPoint._meta.fields
#        if req.POST.get(field.name, "") == ""
#           and field.blank == False]

    missing = []
    if req.POST.get("name","") == "":
        missing.append('name')
    if req.POST.get("code","") == "":
        missing.append('code')
    if req.POST.get("wqmarea","") == "":
        missing.append('wqmarea')


    exists = []
    code = req.POST.get("code","")
    if SamplingPoint.objects.filter( code=code ):
        exists = ['code']

    # TODO: add other validation checks,
    # or integrate proper django forms
    return {
        "missing": missing,
        "exists": exists }


@login_and_domain_required
def add_samplingpoint(request):
    template_name = "samplingpoints.html"
    if request.method == 'POST': # If the form has been submitted...
        form = SamplingPointForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            # saving the form data is not cleaned
            form.save()
            return message(request,
                        "SMS Notification Added",
                        link="/samplingpoints")
    else:
        form = SamplingPointForm() # An unbound form

    return render_to_response(request,template_name, {
        'form': form,
    })

@require_http_methods(["GET", "POST"])
@login_and_domain_required
def delete_samplingpoints(req, pk):
    point = get_object_or_404(SamplingPoint, pk=pk)
    point.delete()

    transaction.commit()
    id = int(pk)
    return message(req,
        "Sampling point %d deleted" % (id),
        link="/samplingpoints")

def comma(string_or_list):
    """ TODO - this could probably go in some sort of global util file """
    if isinstance(string_or_list, basestring):
        string = string_or_list
        return string
    else:
        list = string_or_list
        return ", ".join(list)

@login_and_domain_required
def mapindex(req):
    samplingpoints = SamplingPoint.objects.all().order_by('wqmarea__name','name')
#    counting the number of abnormal range values..
#    Get the abnormal values from the sample submitted.
    counts = []
    if req.method == 'POST':
            form = DateForm(req.POST)
            if form.is_valid():
                start = form.cleaned_data["startdate"]
                end = form.cleaned_data["enddate"]
#                failure = req.POST.get("failure","")

                samples = Sample.objects.filter(sampling_point__in = samplingpoints)
                samples = samples.filter(date_received__range =(start, end))
#                points = samplingpoints
    else:
        form = DateForm()
        for samplingpoint in samplingpoints:
            samples = Sample.objects.filter(sampling_point__in = samplingpoints)
#        points = samplingpoints

    for point in samplingpoints:
        counts.append({"count": Sample.objects.filter(sampling_point = point).count()})             
    
    return render_to_response(req,'wqm/index.html', {
        'samplingpoints': samplingpoints,
        'form': form,
        'counts': counts,
        'content': render_to_string('wqm/samplepoints.html', {'samplingpoints': samplingpoints}),
    })