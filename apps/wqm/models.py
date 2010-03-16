import datetime
from django.db import models
from locations.models import Location


# TODO:  make the modified fields accept blank and null
# so as to accept adding without a modified date.

class WqmAuthority(Location):
    modified = models.DateTimeField(blank=True,null=True)
    created = models.DateTimeField(default=datetime.datetime.now())

    def __unicode__(self):
        return self.name

class WqmArea(Location):
    wqmauthority = models.ForeignKey(WqmAuthority)
    modified = models.DateTimeField(blank=True,null=True)
    craeted = models.DateTimeField(default=datetime.datetime.now())

    def __unicode__(self):
        return self.name

class SamplingPoint(Location):
    wqmarea = models.ForeignKey(WqmArea)
    modified = models.DateTimeField(blank=True,null=True)
    craeted = models.DateTimeField(default=datetime.datetime.now())
