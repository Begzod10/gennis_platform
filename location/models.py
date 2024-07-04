from django.db import models

from system.models import System


# Create your models here.


class Location(models.Model):
    name = models.CharField()
    number = models.IntegerField()
    system = models.ForeignKey(System, on_delete=models.CASCADE, blank=True, null=True)
