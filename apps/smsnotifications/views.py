from django.http import HttpResponse
from django.http import HttpResponseRedirect, Http404
from django.template import RequestContext
from django.shortcuts import get_object_or_404
from django.db.models.query_utils import Q
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from rapidsms.webui.utils import render_to_response, paginated
from domain.decorators import login_and_domain_required
from wqm.models import WqmAuthority, SamplingPoint
from smsnotifications.models import SmsNotification #, NotificationChoice
#from smsnotifications.forms import SmsNotificationForm

#logger_set = False

# temporary placed here, need to move back to forms.py
from django.forms import ModelForm

class SmsNotificationForm(ModelForm):
    class Meta:
        model = SmsNotification
        exclude = ('modified','created',)

@login_and_domain_required
def index(request):
    template_name = 'sindex.html'

    notifications = SmsNotification.objects.all()
    points = SamplingPoint.objects.all().order_by("name")
    districts = WqmAuthority.objects.all()

    return render_to_response(request,
        template_name, {
        "notifications": paginated(request, notifications, prefix="smsnotice"),
        "points" : points,
        "districts":    districts,
    })


@login_and_domain_required
def delete_notifications(req, pk):
    notification = get_object_or_404(SmsNotification, pk=pk)
    notification.delete()

    transaction.commit()
    id = int(pk)
    return message(req,
        "SMS Notification %d deleted" % (id),
        link="/smsnotification")

def check_notice_form(req):

    # verify that all non-blank
    # fields were provided
    missing = [
        field.verbose_name
        for field in SmsNotification._meta.fields
        if req.POST.get(field.name, "") == ""
           and field.blank == False]

    # simple hack to removed a created date in the missing field
    # it's not null but auto-created.
    if 'created' in missing:
        index = missing.index('created')
        del missing[index]

    exists = []
    point = req.POST.get("sampling_point","")
    tester = req.POST.get("authorised_sampler","")
    notice_type = req.POST.get("notification_type","")
    if SmsNotification.objects.filter( sampling_point = point, authorised_sampler = tester, notification_type = notice_type  ):
        exists = ['SmsNotification']

    # TODO: add other validation checks,
    # or integrate proper django forms
    return {
        "missing": missing,
        "exists": exists }

def comma(string_or_list):
    """ TODO - this could probably go in some sort of global util file """
    if isinstance(string_or_list, basestring):
        string = string_or_list
        return string
    else:
        list = string_or_list
        return ", ".join(list)

def get_tester(current_user):
    # todo: get the testers in the system with the same
    # domain as the login user.
    rep_profile = ReporterProfile.objects.filter(domain=current_user.selected_domain)
    reporters = []

    if rep_profile:
        for rep in rep_profile:
            reporter = rep.reporter
            reporters.append(reporter)
    return reporters

@login_and_domain_required
def add_notifications(request):
    template_name = "sms-notifications.html"
    if request.method == 'POST': # If the form has been submitted...
        form = SmsNotificationForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            # saving the form data is not cleaned
            form.save()
            return message(request,
                        "SMS Notification Added",
                        link="/smsnotification")
    else:
        form = SmsNotificationForm() # An unbound form

    return render_to_response(request,template_name, {
        'form': form,
    })

@login_and_domain_required
def edit_notifications(request, pk):
    template_name = "sms-notifications.html"
    notification = get_object_or_404(SmsNotification, pk=pk)
    if request.method == 'POST': # If the form has been submitted...
        form = SmsNotificationForm(request.POST, instance = notification) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            # saving the form data is not cleaned
            notification.delete()
            form.save()
            return message(request,
                        "SMS Notification Updated",
                        link="/smsnotification")
    else:
        form = SmsNotificationForm(instance=notification)
    
    return render_to_response(request,template_name, {
        'form': form,
        'notification': notification,
    })
