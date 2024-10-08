from django.db import models

from system.models import System


class Location(models.Model):
    name = models.CharField()
    number = models.CharField(null=True)
    system = models.ForeignKey(System, on_delete=models.SET_NULL, blank=True, null=True)
    old_id = models.IntegerField(unique=True, null=True)
