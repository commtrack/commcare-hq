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
register = template.Library()

from graphing.models import RawGraph

import time

from samples.models import *
from wqm.models import *

xmldate_format= '%Y-%m-%dT%H:%M:%S'
output_format = '%Y-%m-%d %H:%M'



@register.simple_tag
def get_tester(user):
    # todo: get the testers in the system with the same
    # domain as the login user.
    extuser = ExtUser.objects.get(id=user.id)
    rep_profile = ReporterProfile.objects.filter(domain=extuser.domain)
    reporters = []

    if rep_profile:
        for rep in rep_profile:
            reporter = rep.reporter
            reporters.append(reporter)
    return reporters

def _get_class(count):
    if count % 2 == 0:
        return "even"
    return "odd"

@register.simple_tag
def get_samples(user):
    # TODO: Get all the tester in the same domain and display them
    # with the total samples.
    testers = get_tester(user)

    ret = ''
    ret += '''<table>\n<thead><tr>
            <th>Sampling point (Area)</th>
            <th>Taken by</th>
            <th>Date Taken</th>
            <th>Date Received</th>
            <th>Results</th></tr></thead>'''


    # samples are listed accourding to the tester,
    # wheras according to the received date is more appropriate.
    samples = []
    for tester in testers:
        some_samples = Sample.objects.filter(taken_by=tester)
        samples.extend(some_samples)

    ret += '<tbody>'
    count = 1
    if samples:
        for sample in samples:
            ret += '\n<tr class="%s">' % _get_class(count)
            count += 1
            point = sample.sampling_point
            ret += '<td>%s (%s)</td>' % (point, point.wqmarea)
            ret += '<td>%s</td>' % (sample.taken_by)


            ret += '<td>%s</td>' % (sample.date_taken)
            ret += '<td>%s</td>' % (sample.date_received)

            # TODO: Get the results for the sample and
            # present it in a gud way.
            results = MeasuredValue.objects.filter(sample=sample)
            if results:
                for result in results:
                    ret += '<td>%s %s</td>' % (result.parameter.test_name_short, result.value,)
            else:
                ret += '<td>%s</td>' % ('results')
            ret += '</tr>'
    else:
        ret += '<td>No samples submitted</td>'
    ret += '</tbody></table>'
    return ret