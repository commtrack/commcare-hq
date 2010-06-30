import logging
import hashlib
import settings
import traceback
import sys
import os
import uuid
import string
from datetime import timedelta, datetime
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
from wqm.forms import SamplingPointForm, DateForm
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

@require_http_methods(["GET", "POST"])
@login_and_domain_required
def edit_samplingpoints(req, pk):
    point = get_object_or_404(SamplingPoint, pk=pk)
    
    point_types = SamplingPoint.POINT_TYPE_CHOICES
    point_type_list = []
    # creating a list of point types from sampling point choices.
    for pnt in point_types:
        point_type_list.append(pnt[0])
    
    treatment_choices = SamplingPoint.TREATEMENT_CHOICES
    treatment_choices_list = []
    
    for treatment in treatment_choices:
        treatment_choices_list.append(treatment[0])
    
    delivary_system = DelivarySystem.objects.all()
    
    def get(req):
        return render_to_response(req,
            "samplingpoints.html", {

                # display paginated sampling points
                "points": paginated(req, SamplingPoint.objects.all()),
                "districts": WqmAuthority.objects.all(),
                "point": point,
                "areas": WqmArea.objects.all(),
                "point_types" : point_type_list,
                "treatments" : treatment_choices_list,
                "delivary_system":delivary_system,
                })

    @transaction.commit_manually
    def post(req):

        # if DELETE was clicked... delete
        # the object, then and redirect
        if req.POST.get("delete", ""):
            pk = point.pk
            point.delete()

            transaction.commit()
            return message(req,
                "Sampling Point %d deleted" % (pk),
                link="/samplingpoints")

        else:
            # check the form for errors (just
            # missing fields, for the time being)
            point_errors = check_point_form(req)

            # if any fields were missing, abort. this is
            # the only server-side check we're doing, for
            # now, since we're not using django forms here
            # Note: Shuld put an exist error for the sampling code
            # as no than one point can have same code.
            missing = point_errors["missing"]
            if missing:
                transaction.rollback()
                return message(req,
                    "Missing Field(s): %s" %
                        ", ".join(missing),
                    link="/samplingpoints/%s" % (point.pk))

            try:
                # automagically update the fields of the
                # update_via_querydict(SamplingPoint, req.POST).save()
                latitude = req.POST.get("latitude","")
                if latitude == "":
                    latitude = None
                longitude = req.POST.get("longitude","")
                if longitude == "":
                    longitude = None
                delivary_sys = DelivarySystem.objects.get(pk = req.POST.get("delivary_system",""))
                
                point.name = req.POST.get("name","")
                point.code = req.POST.get("code","")
                point.latitude = latitude
                point.longitude = longitude
                point.wqmarea = WqmArea.objects.get(pk = req.POST.get("wqmarea",""))
                point.delivary_system = delivary_sys
                point.treatement = req.POST.get("treatments","")
                point.point_type = req.POST.get("point_type","")
                # no exceptions, so no problems
                # commit everything to the db
                
                point.save()
                transaction.commit()
                
                return message(req,
                    "Sampling point %d updated" % (point.pk),
                    link="/samplingpoints")

            except Exception, err:
                transaction.rollback()
                raise

    # invoke the correct function...
    # this should be abstracted away
    if   req.method == "GET":  return get(req)
    elif req.method == "POST": return post(req)

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

@require_http_methods(["GET", "POST"])
@login_and_domain_required
def add_samplingpoint(req):
    point_types = SamplingPoint.POINT_TYPE_CHOICES
    point_type_list = []
    # creating a list of point types from sampling point choices.
    for pnt in point_types:
        point_type_list.append(pnt[0])
    
    treatment_choices = SamplingPoint.TREATEMENT_CHOICES
    treatment_choices_list = []
    
    for treatment in treatment_choices:
        treatment_choices_list.append(treatment[0])
    
    delivary_system = DelivarySystem.objects.all()
    def get(req):
        return render_to_response(req,
            "samplingpoints.html", {

                # display paginated sampling points
                "points": paginated(req, SamplingPoint.objects.all()),
                "districts": WqmAuthority.objects.all(),
                "point_types" : point_type_list,
                "treatments" : treatment_choices_list,
                "delivary_system":delivary_system,
                "areas": WqmArea.objects.all(),
                })

    @transaction.commit_manually
    def post(req):
        # check the form for errors (just
        # missing fields, for the time being)
        point_errors = check_point_form(req)

        # if any fields were missing, abort. this is
        # the only server-side check we're doing, for
        # now, since we're not using django forms here
        missing = point_errors["missing"]
        exists = point_errors["exists"]
        if missing:
            transaction.rollback()
            return message(req,
                "Missing Field(s): %s" % comma(missing),
                link="/samplingpoints/add")

        # if code exists, abort.
        if exists:
            transaction.rollback()
            return message(req,
                "Field(s) already exist: %s" % comma(exists),
                link="/samplingpoints/add")

        try:
            # automagically update the fields of the
            # reporter object, from the form
            # update_via_querydict(SamplingPoint, req.POST).save()
            latitude = req.POST.get("latitude","")
            if latitude == "":
                latitude = None
            longitude = req.POST.get("longitude","")
            if longitude == "":
                longitude = None
            name = req.POST.get("name","")
            ## some errrrors here.
            wqmarea = WqmArea.objects.get(pk = req.POST.get("wqmarea",""))
            delivary_sys = DelivarySystem.objects.get(pk = req.POST.get("delivary_system",""))
            
            SamplingPoint(  name = req.POST.get("name",""),
                            code = req.POST.get("code",""),
                            latitude = latitude ,
                            longitude = longitude,
                            delivary_system = delivary_sys,
                            treatement = req.POST.get("treatments",""),
                            point_type = req.POST.get("point_type",""),
                            wqmarea = wqmarea,).save()

            # no exceptions, so no problems
            # commit everything to the db
            transaction.commit()

            # full-page notification
            return message(req,
                "Sampling point %s Added" % (name,),
                link="/samplingpoints")

        except Exception, err:
            transaction.rollback()
            raise

    # invoke the correct function...
    # this should be abstracted away
    if   req.method == "GET":  return get(req)
    elif req.method == "POST": return post(req)

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

#@login_and_domain_required
#def mapindex(req):
#    query = SamplingPoint.objects.all()
#    if req.method == 'POST': # If the form has been submitted...
#        form = DateForm(req.POST) # A form bound to the POST data
#        if form.is_valid(): # All validation rules pass
#            # Process the data in form.cleaned_data
#            # convert the dates into datetime.date()
#            start = datetime.date(form.cleaned_data["startdate"])
#            end = datetime.date(form.cleaned_data["enddate"])
#
#            faliure = req.POST.get("failure","")
#
#            query2 = Sample.objects.filter(date_received__range(start, end))
#            if faliure:
#                # filter out result show only failures
#                pass
#
#            query2.distinct(sampling_point)
#            samplingpoints = query2.sampling_point
#            return render_to_response(req,'wqm/index.html', {
#                'samplingpoints': samplingpoints,
#                'counts': counts,
#                'form': form,
#                'content': render_to_string('wqm/samplepoints.html', {'samplingpoints': samplingpoints}),
#            })
#    else:
#        form = DateForm() # An unbound form
#
#    counts = []
#    for point in query:
#        if (point.id) == None:
#            counts[ point.id ] = Sample.objects.filter(sampling_point = point).count()
#
#    samplingpoints = query.order_by("name")
#    #'counts': counts,
#    #'form': form,
#    return render_to_response(req,'wqm/index.html', {
#        'samplingpoints': samplingpoints,
#        'content': render_to_string('wqm/samplepoints.html', {'samplingpoints': samplingpoints}),
#    })

@login_and_domain_required
def mapindex(req):
    samplingpoints = SamplingPoint.objects.all().order_by('wqmarea__name','name')

#    counting the number of abnormal range values..
#    Get the abnormal values from the sample submitted.
    points = []
    counts = {}
    if req.method == 'POST':
            form = DateForm(req.POST)
            if form.is_valid():
                start = datetime.date(form.cleaned_data["startdate"])
                end = datetime.date(form.cleaned_data["enddate"])
#                failure = req.POST.get("failure","")

                for samplingpoint in samplingpoints:
                    samples = Sample.objects.filter(sampling_point = samplingpoint)
                    samples.filter(date_received__range =(start, end))

                    counts[samplingpoint.id] = {"count": samples.count()}
                    points.append(samplingpoint)
            else:
                form = DateForm()

    if req.method != 'POST':
        form = DateForm()
        for samplingpoint in samplingpoints:
            samples = Sample.objects.filter(sampling_point = samplingpoint)
            counts[samplingpoint.id] = {"count": samples.count()}
            points.append(samplingpoint)

#            for sample in samples:
#                m_values = MeasuredValue.objects.filter(sample = sample)
#                for value in m_values:
#                    abnormal_range = AbnormalRange.objects.get(value_rule__parameter = value.parameter)
#                    min = abnormal_range.minimum
#                    max = abnormal_range.maximum
#                    if value.value in range(min,max):
#                        abnormal_values[samplingpoint.id] = abnormal_values[samplingpoint.id] + abnormal_range.count()
                
    return render_to_response(req,'wqm/index.html', {
        'samplingpoints': points,
        'form': form,
        'counts': counts,
        'content': render_to_string('wqm/samplepoints.html', {'samplingpoints': samplingpoints}),
    })