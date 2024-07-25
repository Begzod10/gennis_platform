from django.db import models
from group.models import Group
from teachers.models import Teacher
from django.conf import settings


class ObservationInfo(models.Model):
    title = models.CharField(max_length=100)

    class Meta:
        ordering = ['id']


class ObservationOptions(models.Model):
    name = models.CharField(max_length=100)
    value = models.IntegerField()

    class Meta:
        ordering = ['id']


class ObservationDay(models.Model):
    day = models.DateTimeField()
    average = models.IntegerField()
    comment = models.CharField(max_length=100)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='observation_day_user')
    group = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True, related_name='observation_group')
    teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, related_name='observation_teacher')
    deleted = models.BooleanField(default=False)

    class Meta:
        ordering = ['id']


class ObservationStatistics(models.Model):
    comment = models.CharField(max_length=100)
    observation_day = models.ForeignKey(ObservationDay, on_delete=models.SET_NULL, null=True,
                                        related_name='observation_statistics_observation_day')
    observation_info = models.ForeignKey(ObservationInfo, on_delete=models.SET_NULL, null=True,
                                         related_name='observation_statistics_observation_info')
    observation_option = models.ForeignKey(ObservationOptions, on_delete=models.SET_NULL, null=True,
                                           related_name='observation_statistics_observation_option')

    class Meta:
        ordering = ['id']
