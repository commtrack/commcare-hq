from django.db import models
from locations.models import Location
from datetime import datetime
from standards.models import Standard, WaterUseType
from reporters.models import Reporter
from wqm.models import SamplingPoint
from datetime import datetime

# Create your Django models here, if you need them.

class Parameter(models.Model):
    test_name = models.CharField(max_length=120)
    unit = models.CharField(max_length=50, null=True, blank=True)
    lookup_hint = models.BooleanField()
    test_name_short = models.CharField(max_length=20)
    modifed = models.DateTimeField(blank=True, null=True, default=datetime.now())

    def __unicode__(self):
        return self.test_name

class MeasuredValue(models.Model):
    '''
    The measured values
    '''
    parameter = models.ForeignKey(Parameter)
    # shuld be a charfield but for now it's a decimalfield.
    value = models.CharField(max_length=20, help_text='the value measured')
    #value = models.DecimalField(max_digits=8, decimal_places=2)
    modified = models.DateTimeField(blank=True, null=True)
    created = models.DateTimeField(default=datetime.now())

    def __unicode__(self):
        return '%s' % (self.value)


class Sample(models.Model):
    '''
    This is sample
    '''
    taken_by = models.ForeignKey(Reporter)
    sampling_point = models.ForeignKey(SamplingPoint)
    notes = models.TextField(null=True, blank=True)
    measured_values = models.ForeignKey(MeasuredValue)
    date_taken = models.DateTimeField()
    date_received = models.DateTimeField()
    created = models.DateTimeField()
    modified = models.DateTimeField(blank=True, null=True)

    def __unicode__(self):
        return self.notes


class ValueRule(models.Model):
    '''
    Rules Applied to the values
    '''
    description = models.TextField()
    parameter = models.ForeignKey(Parameter)
    standard = models.ForeignKey(Standard)
    water_use_type = models.ForeignKey(WaterUseType)
    modified = models.DateTimeField(blank=True, null=True)
    created = models.DateTimeField(default=datetime.now() )

    def __unicode__(self):
        return self.description

class NormalRange(models.Model):
    '''
    Normal range for values.
    '''
    description = models.CharField(max_length=200)
    value_rule = models.ForeignKey(ValueRule)
    maximum = models.IntegerField()
    minimum = models.IntegerField()
    modified = models.DateTimeField(blank=True, null=True)
    created = models.DateTimeField(default=datetime.now())

    def __unicode__(self):
        return '%d - %d' % (self.minimum, self.maximum)

class AbnormalRange(models.Model):
    description = models.CharField(max_length=200)
    value_rule = models.ForeignKey(ValueRule)
    maximum = models.IntegerField()
    minimum = models.IntegerField()
    remedialaction = models.CharField(max_length=20)
    color = models.CharField(max_length=25)
    modified = models.DateTimeField(blank=True, null=True)
    created = models.DateTimeField()

    def __unicode__(self):
        return '%d - %d' % (self.minimum, self.maximum)
    