from django.contrib import admin
from samples.models import *

'''
'''
class MeasuredValueInline(admin.TabularInline):
    model = MeasuredValue
    extra = 3

class SampleAdmin(admin.ModelAdmin):
    list_display = ('taken_by','sampling_point','notes')
    inlines = [MeasuredValueInline]
admin.site.register(Sample, SampleAdmin)
#admin.site.register(Sample)

#class ParameterAdmin(admin.ModelAdmin):
#    list_display = ('test_name','unit','lookup_hint','test_name_short')
#    search_fields = ('test_name','unit','lookup_hint','test_name_short')
#admin.site.register(Parameter, ParameterAdmin)
admin.site.register(Parameter)

#admin.site.register(MeasuredValue)
admin.site.register(ValueRule)
admin.site.register(NormalRange)
admin.site.register(AbnormalRange)