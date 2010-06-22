from django.db import models
from datetime import datetime




class SyncEvent(models.Model):
    event_id = models.URLField()
    date = models.DateTimeField()
    contents = models.TextField()
    status = models.BooleanField(default=False)

def get_id():
    today = datetime.today()
    a = SyncEvent.objects.filter(   date__day = today.day,
                                        date__month = today.month,
                                        date__year = today.year)
    content =''
    for i in a:
        content += '%s' % i.event_id
    return content