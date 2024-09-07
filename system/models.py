from django.db import models

from django.db.models.signals import post_migrate
from django.dispatch import receiver


# Create your models here.
class System(models.Model):
    """ center, school, institute ... """
    name = models.CharField(max_length=255)
    number = models.IntegerField()
    type = models.CharField(null=True)


@receiver(post_migrate)
def create_default_overhead_types(sender, **kwargs):
    default_values = [{"name": "center", "number": 1},
                      {"name": "school", "number": 2}]
    for value in default_values:
        System.objects.get_or_create(name=value['name'], number=value['number'], type=value['type'])
