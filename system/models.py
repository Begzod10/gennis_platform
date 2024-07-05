from django.db import models


# Create your models here.
class System(models.Model):
    """ center, school, institute ... """
    name = models.CharField(max_length=255)
    number = models.IntegerField()

    def __str__(self):
        return self.name



