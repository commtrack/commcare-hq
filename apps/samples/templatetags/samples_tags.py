import datetime
from django import template

from django.core.urlresolvers import reverse
from django.template.loader import render_to_string
from django.db.models.query_utils import Q

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
from wqm.models import SamplingPoint, WqmArea, WqmAuthority

import time

from samples.models import MeasuredValue, Sample
from wqm.models import *

xmldate_format= '%Y-%m-%dT%H:%M:%S'
output_format = '%Y-%m-%d %H:%M'


@register.simple_tag
def m_values(this_sample):
    # TODO: Get all the tester in the same domain and display them
    # with the total samples.
    
    ret = ''
    results = MeasuredValue.objects.filter(sample= this_sample)
    if results:
        ret += '<td>'
        for result in results:
            ret += '%s %s%s, <br />' % (result.parameter.test_name, result.value,result.parameter.unit)
        ret += '</td>'
    else:
        ret += '<td>%s</td>' % ('No parameter for this submitted sample')
    
    return ret

#@register.simple_tag
#def get_tester(user):
#    # todo: get the testers in the system with the same
#    # domain as the login user.
#    rep_profile = ReporterProfile.objects.filter(domain=user.selected_domain)
#    reporters = []
#
#    if rep_profile:
#        for rep in rep_profile:
#            reporter = rep.reporter
#            reporters.append(reporter)
#    return reporters
#
#def _get_class(count):
#    if count % 2 == 0:
#        return "even"
#    return "odd"
#
#
#@register.simple_tag
#def get_samples(user, districts):
#    # TODO: Get all the tester in the same domain and display them
#    # with the total samples.
#    testers = get_tester(user)
#
#    ret = ''
#    ret += '''<table>\n<thead><tr>
#            <th>Sampling point (Area)</th>
#            <th>Taken by</th>
#            <th>Date Taken</th>
#            <th>Date Received</th>
#            <th>Results</th></tr></thead>'''
#
#
#    # samples are listed according to the received date,
#    # filter in districts and tester in the domain
#    districts_ids = []
#    for d in districts:
#        districts_ids.append(d.id)
#        
#    samples = []
#    query = Sample.objects.filter(taken_by__in=testers)
#    query = query.filter(sampling_point__wqmarea__wqmauthority__in = districts_ids)
#    some_samples = query
#    samples.extend(some_samples)
#    
#    ret += '<tbody>'
#    count = 1
#    if samples:
#        for sample in samples:
#            ret += '\n<tr class="%s">' % _get_class(count)
#            count += 1
#            point = sample.sampling_point
#            ret += '<td>%s (%s)</td>' % (point, point.wqmarea)
#            ret += '<td>%s</td>' % (sample.taken_by)
#
#            ret += '<td>%s</td>' % (sample.date_taken)
#            ret += '<td>%s</td>' % (sample.date_received)
#
#            # TODO: Get the results for the sample and
#            # present it in a gud way.
#            results = MeasuredValue.objects.filter(sample=sample)
#            if results:
#                ret += '<td>'
#                for result in results:
#                    ret += '%s %s%s, <br />' % (result.parameter.test_name, result.value,result.parameter.unit)
#                ret += '</td>'
#            else:
#                ret += '<td>%s</td>' % ('No parameter for this submited sample')
#            ret += '</tr>'
#    else:
#        ret += '<td>No samples submitted</td>'
#    ret += '</tbody></table>'
#    return ret