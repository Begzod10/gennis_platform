from django.db import models


class Language(models.Model):
    name = models.CharField(null=False, blank=False, max_length=250)
    old_id = models.IntegerField(unique=True, null=True)

    def __str__(self):
        return self.name
