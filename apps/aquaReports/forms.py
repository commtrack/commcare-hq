from django import forms
from django.db import models
from django.forms import ModelForm
from django.contrib.admin import widgets

from wqm.models import SamplingPoint
from reporters.models import Reporter
from samples.models import Parameter

class SelectSamplingPointForm(forms.Form):
    sampling_points = forms.ModelMultipleChoiceField(queryset=SamplingPoint.objects.all(),
                                                    help_text="Hold down Ctrl for multple selection")

class SelectTesterForm(forms.Form):
    testers = forms.ModelMultipleChoiceField(queryset=Reporter.objects.all(),
                                            help_text="Hold down Ctrl for multple selection")
    
class SelectParameterForm(forms.Form):
    parameters = forms.ModelMultipleChoiceField(queryset=Parameter.objects.all(),
                                               help_text="Hold down Ctrl for multple selection")

class DateForm(forms.Form):
    startdate = forms.DateField(widget = widgets.AdminDateWidget())
    enddate = forms.DateField(widget = widgets.AdminDateWidget())