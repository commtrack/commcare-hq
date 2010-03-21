from datetime import datetime

from django.db import models
from django.db.models.signals import post_save

from locations.models import Location
from standards.models import Standard, WaterUseType
from reporters.models import Reporter
from wqm.models import SamplingPoint
from xformmanager.models import Metadata


# Create your Django models here, if you need them.
H2S_XMLNS = "http://www.aquatest-za.org/h2s"
PHYSCHEM_XMLNS = "http://www.aquatest-za.org/physchem"
SAMPLE_XMLNS = [H2S_XMLNS, PHYSCHEM_XMLNS]

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
    measured_values = models.ForeignKey(MeasuredValue, null=True, blank=True) # TODO: don't allow null!!!
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
    
    

def check_and_add_sample(sender, instance, created, **kwargs): #get sender, instance, created
    # only process newly created forms, not all of them
    if not created:             return
    
    # check the form type to see if it is a new sample
    form_xmlns = instance.formdefmodel.target_namespace
    
    if form_xmlns in SAMPLE_XMLNS:
        # it is an xmlns we care about, so make a new sample
        sample_data = instance.formdefmodel.row_as_dict(instance.raw_data)
                
        now = datetime.now()
        # start with measured value
        val = MeasuredValue()
        val.parameter = Parameter.objects.all()[0]
        val.value = sample_data["h2s_test_testresults_h2s"]
        val.modified = now
        val.created = now
        val.save()
        
        sample = Sample()
        # sample.taken_by = None # TODO: look up reporter from     
        sample.taken_by = Reporter.objects.get(id = 1)
        sample.sampling_point = SamplingPoint.objects.all()[0] # get the point from a point code
        sample.notes = sample_data["h2s_test_datacapture_comments"]
        sample.measured_values = val
        sample.date_taken = sample_data["h2s_test_assessment_assessmentdate"]
        sample.date_received = instance.attachment.submission.submit_time
        sample.created = now
        sample.modified = now
        # TODO: save when all fields are filled in
        sample.save()
        
    
    

# Register to receive signals each time a Metadata is saved
post_save.connect(check_and_add_sample, sender=Metadata)