from django.db import models

from location.models import Location


class Branch(models.Model):
    name = models.CharField(max_length=255)
    number = models.CharField(null=True)
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, blank=True, null=True)
    location_text = models.CharField(max_length=255, null=True)
    map_link = models.CharField(null=True, blank=True)
    code = models.IntegerField(null=True)
    phone_number = models.CharField(max_length=20, null=True)
    director_fio = models.CharField(max_length=255, null=True)
    location_type = models.CharField(max_length=255, null=True)
    district = models.CharField(max_length=255, null=True)
    bank_sheet = models.CharField(null=True)
    inn = models.CharField(max_length=255, null=True)
    bank = models.CharField(max_length=255, null=True)
    mfo = models.CharField(max_length=50, null=True)
    campus_name = models.CharField(max_length=255, null=True)
    address = models.CharField(max_length=255, null=True)
    year = models.DateField(null=True)
    old_id = models.IntegerField(unique=True, null=True)
