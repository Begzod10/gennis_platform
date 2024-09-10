from django.db import models

from django.db.models.signals import post_migrate
from django.dispatch import receiver


# Create your models here.
class System(models.Model):
    """ center, school, institute ... """
    name = models.CharField(max_length=255)
    number = models.IntegerField()


@receiver(post_migrate)
def create_default_overhead_types(sender, **kwargs):
<<<<<<< HEAD
    default_values = [{"name": "center", "number": 1},
                      {"name": "school", "number": 2}]
=======
    default_values = [{"number": 1, 'name': 'center'},
                      {"number": 2, 'name': 'school'}]
>>>>>>> 4ee5700a87d831506ef0cf7a2e904cb71172a50e
    for value in default_values:
        System.objects.get_or_create(name=value['name'], number=value['number'])
