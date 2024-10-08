from django.db import models
from django.contrib.auth.models import Group

from system.models import System
from user.models import CustomUser
from location.models import Location
from branch.models import Branch
from django.conf import settings


class AuthGroupSystem(models.Model):
    group = models.OneToOneField(Group, on_delete=models.CASCADE)
    system_id = models.ForeignKey(System, on_delete=models.CASCADE)
    class Meta:
        ordering = ['id']


class Access(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    auth_group_system = models.ForeignKey(AuthGroupSystem, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)


class ManySystem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='many_systems')
    system = models.ForeignKey(System, on_delete=models.CASCADE)


class ManyLocation(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='many_locations')
    location = models.ForeignKey(Location, on_delete=models.CASCADE)


class ManyBranch(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='many_branches')
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)


class DescriptionForTable(models.Model):
    table_name = models.CharField()
    description = models.CharField()
