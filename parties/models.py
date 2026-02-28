from django.db import models


class Party(models.Model):
    name = models.CharField(max_length=100)
    image = models.FileField(upload_to='parties/')
    desc = models.TextField(null=True, blank=True)
    color = models.CharField(max_length=100, null=True, blank=True)


class PartyTask(models.Model):
    name = models.CharField(max_length=100)
    desc = models.TextField(null=True, blank=True)
    ball = models.IntegerField(null=True, blank=True)
    is_completed = models.BooleanField(default=False)
    parties = models.ManyToManyField(Party)
