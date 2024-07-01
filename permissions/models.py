from django.db import models
from django.contrib.auth.models import Group
from
# Create your models here.
from system.models import System


class AuthGroupSystem(models.Model):
    group = models.OneToOneField(Group, on_delete=models.CASCADE)
    system_id = models.ForeignKey(System, on_delete=models.CASCADE)



# class Access(models.Model):
