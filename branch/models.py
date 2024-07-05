from django.db import models

# Create your models here.

from location.models import Location


class Branch(models.Model):
    name = models.CharField()
    number = models.IntegerField()
    location = models.ForeignKey(Location, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.name, self.number

