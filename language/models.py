from django.db import models


class Language(models.Model):
    name = models.CharField(null=False, blank=False, max_length=250)
