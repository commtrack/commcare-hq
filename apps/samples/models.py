from datetime import datetime

from django.db import models
from django.db.models.signals import post_save

from locations.models import Location
from standards.models import Standard, WaterUseType
from reporters.models import Reporter
from wqm.models import SamplingPoint
from xformmanager.models import Metadata
from hq.models import ReporterProfile


H2S_XMLNS = "http://www.aquatest-za.org/h2s"
PHYSCHEM_XMLNS = "http://www.aquatest-za.org/physchem"
SAMPLE_XMLNS = [H2S_XMLNS, PHYSCHEM_XMLNS]

# TODO: clean up the code.
#class SampleDates(models.Model):
#    """
#        This module adds, modified and created dates for samples modules
#    """
#    modified = models.DateTimeField(blank=True, null=True)
#    created = models.DateTimeField(default=datetime.now())


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
    notes = models.TextField(null=True, blank=True) # TODO: Change this to charfield
    # TODO: measured value should be many-to-many field, coz one sample 
    # may have many test results.
    measured_values = models.ForeignKey(MeasuredValue, null=True, blank=True)
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
        
        sample = Sample()
        now = datetime.now()

        
        # TODO: sampling points should be loaded in the db through a fixture..

        # check for which form submitted and create a sample.
        if form_xmlns == H2S_XMLNS:
            point = SamplingPoint.objects.get(code = sample_data["h2s_test_assessment_pointcode"])
            sample.sampling_point = point
            sample.date_taken = sample_data["h2s_test_assessment_assessmentdate"]
            sample.notes = sample_data["h2s_test_datacapture_comments"]
            sample.date_received = now
            sample.created = now
            
            # check the reporter using he's/her alias
            # TODO: Make sure the reporter is a tester (is have a reporter profile)
            # if he's not a tester(ie does not belong to aquatest domain) issue an error.
            alias = sample_data["h2s_test_datacapture_enteredby"]
            try:
                reporter = Reporter.objects.get(alias = alias)
                # make sure the reporter have a profile for a domain.
                # TODO: Limit the submission to a domain
                reporter_profile = ReporterProfile.objects.get(reporter=reporter)
                # save a reporter with a profile
                sample.taken_by = reporter
            except Exception, e:
                raise

            # generate test result column from the registered paramater
            parameters = Parameter.objects.all()
            # initialise the tests, inorder for the index to eqaul the pk of
            # the parameter. ( a better way of refering to a parameter shuld
            # be looked upon).
            tests = [None] * 100 # TODO: Initialise the tests 
            for para in parameters:
                test = "h2s_test_testresults_" + para.test_name_short
                index = int(para.pk)
                tests.insert(index, test)
                #tests.append(test)

            for some in tests:
                if sample_data.get(some) != None:
                    para_id = tests.index(some)
                    # print " >>>>>>>>>>> index : %s " % tests.index(some)
                    # print Parameter.objects.get(id=tests.index(some))

                    # this test is present in the xform, hence store it's value.
                    value = MeasuredValue()
                    value.value = sample_data[some]

                    # TODO: get a parameter for the value. according to the test done.
                    value.parameter = Parameter.objects.get(id = para_id)
                    value.save()

            

            
            sample.measured_values = value

            #create a sample
            print "creating a sample"
            sample.save()
        
# Register to receive signals each time a Metadata is saved
post_save.connect(check_and_add_sample, sender=Metadata)