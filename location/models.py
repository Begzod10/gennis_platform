from django.db import models
from system.models import System


class Location(models.Model):
    name = models.CharField(max_length=255)
    number = models.CharField(null=True, default=None)
    system = models.ForeignKey(System, on_delete=models.CASCADE, null=True, blank=True)
