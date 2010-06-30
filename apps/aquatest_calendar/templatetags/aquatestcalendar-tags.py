import datetime
from django import template

from django.core.urlresolvers import reverse
from django.template.loader import render_to_string

from django.contrib.contenttypes.models import ContentType
from types import ListType,TupleType

from xformmanager.models import *
import xformmanager.adapter.querytools as qtools
from hq.models import *
import hq.utils as utils
from datetime import timedelta
import graphing.dbhelper as dbhelper
from hq.models import *
from reporters.models import Reporter
from samples.models import Sample
register = template.Library()

from graphing.models import RawGraph

import time

xmldate_format= '%Y-%m-%dT%H:%M:%S'
output_format = '%Y-%m-%d %H:%M'



@register.simple_tag
def days_samples(year, month, day):
    query = Sample.objects.filter(  date_received__day = day,
                                    date_received__month = month,
                                    date_received__year = year)
    samples_to_day = query.count()
    return samples_to_day


@register.simple_tag
def _get_class(count):
    if count % 2 == 0:
        return "even"
    return "odd"
 