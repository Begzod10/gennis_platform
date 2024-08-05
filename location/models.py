from django.db import models

from system.models import System


class Location(models.Model):
    name = models.CharField()
    number = models.CharField(null=True)
    system = models.ForeignKey(System, on_delete=models.CASCADE, blank=True, null=True)
    old_id = models.IntegerField()

    # def __str__(self):
    #     return self.name
