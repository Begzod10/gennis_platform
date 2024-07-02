from django.db import models

# Create your models here.

from system.models import System


class Location(models.Model):
    name = models.CharField()
    number = models.IntegerField()
    system = models.ForeignKey(System, on_delete=models.CASCADE, blank=True, null=True)
