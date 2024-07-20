from django.db import models

from location.models import Location


class Branch(models.Model):
    name = models.CharField(max_length=255)
    number = models.IntegerField()
    location_id = models.ForeignKey(Location, on_delete=models.CASCADE, blank=True, null=True)
    location = models.CharField(max_length=255)
    map_link = models.TextField()
    code = models.IntegerField()
    phone_number = models.CharField(max_length=20)
    director_fio = models.CharField(max_length=255)
    location_type = models.CharField(max_length=255)
    district = models.CharField(max_length=255)
    bank_sheet = models.TextField()
    inn = models.CharField(max_length=255,null=True)
    bank = models.CharField(max_length=255,null=True)
    mfo = models.CharField(max_length=50,null=True)
    campus_name = models.CharField(max_length=255,null=True)
    address = models.CharField(max_length=255,null=True)
    year = models.DateField(null=True)




    # def __str__(self):
    #     return self.name
