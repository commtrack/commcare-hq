import logging
import re, calendar
from calendar import monthcalendar
from datetime import datetime
import datetime
import hashlib
import settings
import traceback
import sys
import os
import uuid
import string
from datetime import datetime
from datetime import timedelta
from graphing import dbhelper

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
from django import forms

from rapidsms.webui.utils import render_to_response, paginated
#from rapidsms.reporters.models import *

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
from reporters.models import Reporter, PersistantBackend, PersistantConnection
from locations.models import Location, LocationType
from wqm.models import WqmAuthority
from calender.utils import *
from samples.models import *
import time
####################################
#
#those imports to be checked and remove unwanted
#
###############################
import datetime, calendar
import copy

#from django.template.loader import get_template
from django.template import Context
from django.http import HttpResponse, HttpResponseRedirect

from aquatest_calendar.controller import CalendarController
from wqm.models import WqmArea
logger_set = False

@login_and_domain_required
def view(request):
    """Calendar view"""

    user = request.user
    date = datetime.datetime.now()
    default = dict(month=date.month, year=date.year, day=1, rowid=1,
            name="", desc="", when="")
    url = request.path
    p = getParams(request, default)
    year, month, day = p['year'], p['month'], p['day']
#    samples = today_samples_data(day,month,year)

    search_string = request.REQUEST.get("q","")
    samples = []
    if search_string == "":
        for i in range(1,calendar.monthrange(year,month)[1]):
    #        dat = datetime.date(year,month,i)
    #    print dat
            day_sample = today_samples_data(datetime.date(year,month,i))
    #        print '%s' % day_sample

            samples.append(day_sample)
    
    else:
        area = WqmArea.objects.get(id = search_string)
        search_string = area
        for i in range(1,calendar.monthrange(year,month)[1]):
            day_sample = today_samples_data_area(datetime.date(year,month,i),area)
            samples.append(day_sample)
#    for i in samples:
#        print '%s'% samples
#    print 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
#    print samples[2]
#    print samples
    # create calendar obj


    areas = WqmArea.objects.all()
    cal = CalendarController(day)
    cal.load(year, month)
    template_name="calendar.html"
    context = {}
    dict(username=user, cal=cal, url=url)
    i = 0
    context = {
        "username":user,
        "cal":cal,
        "url":url,
        'samples':samples,
        "areas":areas,
        "search_string":search_string,
        'i':i
    }
    return render_to_response(request, template_name, context)

def set_css_tag(normality):
    if normality == 0:
        divclasscontet = 'dateHolderDiv'
    elif normality == 1:
        divclasscontet = 'dateHolderDivAb'
    else:
        divclasscontet = 'dateHolderDivMor'
    return divclasscontet

def get_normality(day):
    '''
    returns the number counted of normality value either normal range or abnormal range
    '''
    #this is for testing it should be replaced!
    if day < 11:
        normality = 0
    if day > 10 and day < 21:
        normality = 1
    if day > 20 and day < 31:
        normality = 7

    return normality

def today_samples_data(today):
    a = Sample.objects.filter(      date_taken__day = today.day,
                                    date_taken__month = today.month,
                                    date_taken__year = today.year)
    return a.count()
def today_samples_data_area(today, area):
    a = Sample.objects.filter(  date_received__day = today.day,
                                    date_received__month = today.month,
                                    date_received__year = today.year)
    a.filter(sampling_point__wqmarea = area)
    return a.count()

def addEvent(request):
    """add event to calendar"""
    user = request.user
    default = dict(month=1, year=1, day=1, rowid=1, name="", desc="", when="")
    p = getParams(request, default)
    year, month, day = p['year'], p['month'], p['day']

    # create calendar obj
    cal = CalendarController(day)
    cal.load(year, month)

    # parpare data for adding Event
    whenDate = datetime.date(year, month, day)
    whenTime = datetime.time(*map(int, p['when'].strip().split(':')))
    when = datetime.datetime.combine(whenDate, whenTime)

    # adding Event
    cal.addEvent(day, p['name'], when, p['desc'])

    # show view with new result
    return redirect2view(request.path, year, month, day)


def delEvent(request):
    """delete event from calendar"""
    user = request.user
    default = dict(month=1, year=1, day=1, rowid=1, name="", desc="", when="")
    p = getParams(request, default)
    year, month, day = p['year'], p['month'], p['day']

    # create calendar obj
    cal = CalendarController(day)
    cal.load(year, month)

    # delete Event
    cal.delEvent(day, p['rowid'])

    # show view with new result
    return redirect2view(request.path, year, month, day)


def updEvent(request):
    """update selected event to calendar"""
    user = request.user
    default = dict(month=1, year=1, day=1, rowid=1, name="", desc="", when="")
    p = getParams(request, default)
    year, month, day = p['year'], p['month'], p['day']

    # create calendar obj
    cal = CalendarController(day)
    cal.load(year, month)

    # parpare data for adding Event
    whenDate = datetime.date(year, month, day)
    whenTime = datetime.time(*map(int, p['when'].strip().split(':')))
    when = datetime.datetime.combine(whenDate, whenTime)

    # update Event
    cal.updEvent(day, p['rowid'], p['name'], when, p['desc'])

    # show view with new result
    return redirect2view(request.path, year, month, day)


## helper function
def getParams(request, default):
    """get parameter (case insensitive for key) (support both get and post)
        param is updated as side effect (for now)"""
    paramKeys = ['year', 'month', 'day', 'rowid', 'name', 'desc', 'when']
    paramFunc =  [int, int, int, int, str, str, str ]
    paramDef = dict(zip(paramKeys, paramFunc))

    inputDict = getattr(request, request.method, {})
    result = copy.deepcopy(default)
    for k in inputDict:
        kl = k.lower()
        if kl in default and kl in paramDef:
            try:
                result[kl] = paramDef[kl](getattr(request, request.method)[k])
            except KeyError:
                pass
    return result


def upOneLevelURL(url):
    """eg1:  upOneLevelURL('http://aaa/bbb/ccc') == 'http://aaa/bbb/'
       eg2:  upOneLevelURL('http://aaa/bbb/ccc/') == 'http://aaa/bbb/'
       eg3:  upOneLevelURL('http://aaa/bbb/ccc/?xyz') == 'http://aaa/bbb/'
       eg4:  upOneLevelURL('http://aaa/bbb/ccc?xyz') == 'http://aaa/bbb/'
    """
    sep = '/'
    result = url.split('?')[0]
    if result[-1] == sep:
        result = result[:-1].rsplit(sep, 1)[0]
    else:
        result = result.rsplit(sep, 1)[0]
    return result + sep


def redirect2view(url, year, month, day):
    url = upOneLevelURL(url)
    qstr = '?year=%d&month=%d&day=%d' % (year, month, day)
    url += qstr
    return HttpResponseRedirect(url)


@login_and_domain_required
def sample_popup(request):
    """Popup (compact) view a group of forms for a particular xmlns.
       Used in modal dialogs."""
    user = request.user
#    group = FormDefModel.get_group_for_namespace(request.user.selected_domain, xmlns)
    return render_to_response(request, "xformmanager/xmlns_group_popup.html",
                              {"user": user})



@login_and_domain_required
def new(request):

    template_name="calendarnew.html"
    context = {}

    context = {

    }
    return render_to_response(request, template_name, context)

@login_and_domain_required
def samples_popup(request):
    """Popup (compact) view a group of samples for a particular day.
    """

    user = request.user
    date = datetime.datetime.now()
    default = dict(month=date.month, year=date.year, day=1, rowid=1,
            name="", desc="", when="")
    url = request.path
    p = getParams(request, default)
    year, month, day = p['year'], p['month'], p['day']
#    samples = today_samples_data(day,month,year)

    search_string = request.REQUEST.get("q","")
    samples = []
    if search_string == "":
        for i in range(1,calendar.monthrange(year,month)[1]):
    #        dat = datetime.date(year,month,i)
    #    print dat
            day_sample = today_samples_data(datetime.date(year,month,i))
    #        print '%s' % day_sample

            samples.append(day_sample)
    
    else:
        area = WqmArea.objects.get(id = search_string)
        search_string = area
        for i in range(1,calendar.monthrange(year,month)[1]):
            day_sample = today_samples_data_area(datetime.date(year,month,i),area)
            samples.append(day_sample)
#    for i in samples:
#        print '%s'% samples
#    print 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
#    print samples[2]
    print samples
    # create calendar obj


    areas = WqmArea.objects.all()
    cal = CalendarController(day)
    cal.load(year, month)
    template_name="sample_popup.html"
    context = {}
    dict(username=user, cal=cal, url=url)
    i = 0
    context = {
        "username":user,
        "cal":cal,
        "url":url,
        'samples':samples,
        "areas":areas,
        "search_string":search_string,
        'i':i
    }

    return render_to_response(request, template_name,context)