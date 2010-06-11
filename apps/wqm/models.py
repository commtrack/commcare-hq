import datetime
#from django.db import models
from django.contrib.gis.db import models

from locations.models import Location

class WqmLocation(Location):
    """
    For this module, we add a created and modified date to 
    our locations.
    """ 
#    location_simple_type = models.CharField(max_leght=10,blank=True, null=True)
    modified = models.DateTimeField(blank=True,null=True)
    created = models.DateTimeField(default=datetime.datetime.now())

    # GeoDjango-specific: a geometry field (MultiPolygonField), and
    # overriding the default manager with a GeoManager instance.
#    area_covered = models.MultiPolygonField()
#    objects = models.GeoManager()

class WqmAuthority(WqmLocation):
    """E.g. a district"""
    
    def __unicode__(self):
        return self.name

class WqmArea(WqmLocation):
    wqmauthority = models.ForeignKey(WqmAuthority)
    
#    def save(self, **kwargs):
#        WqmArea.location_simple_type='WqmArea'
#        super(MasterIndex, self).save(**kwargs)
    
    def __unicode__(self):
        return self.name

class DelivarySystem(models.Model):
    name = models.CharField(max_length=100, 
                            help_text="house connection, public tap, borehole, protected spring, unprotected spring, river, dam or lake, reservoir,distribution system")
    
    def __unicode__(self):
        return self.name
    
class SamplingPoint(WqmLocation):
    """ The point the tests are done """
    POINT_TYPE_CHOICES = (
                                  ("ground", "Ground"),
                                  ("surface","Surface"),
                                  )
    TREATEMENT_CHOICES = (
                          ('treated', 'Treated'),
                          ('untreated', 'Untreated'),
                          )
    wqmarea = models.ForeignKey(WqmArea)
    point_type = models.CharField(max_length=30, choices=POINT_TYPE_CHOICES)
    delivary_system = models.ForeignKey(DelivarySystem)
    treatement = models.CharField(max_length=30, choices=TREATEMENT_CHOICES)
    point = models.PointField(null=True, blank=True)
    objects = models.GeoManager()

    def __unicode__(self):
        return self.name
