from django.db import models
from group.models import Group
from teachers.models import Teacher
from django.conf import settings
from django.db.models.signals import post_migrate
from django.dispatch import receiver


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
    day = models.DateField()
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


@receiver(post_migrate)
def create_default_overhead_types(sender, **kwargs):
    default_values = [
        {
            "title": "Teacher follows her or his lesson plan"
        },
        {
            "title": "Teacher is actively circulating in the room"
        },
        {
            "title": "Teacher uses feedback to encourage critical thinking"
        },
        {
            "title": "Students are collaborating with each other and engaged in"
        },
        {
            "title": "Teacher talking time is 1/3"
        },
        {
            "title": "Teacher uses a variety of media and resources for learning"
        },
        {
            "title": "Teacher uses different approach of method"
        },
        {
            "title": "Teacher has ready made materials for the lesson"
        },
        {
            "title": "Lesson objective is present and communicated to students",

        }
    ]
    for value in default_values:
        ObservationInfo.objects.get_or_create(title=value['title'])
    options = [
        {
            "name": "Missing",
            "value": 1
        },
        {
            "name": "Done but poorly",
            "value": 2
        },
        {
            "name": "Acceptable",
            "value": 3
        },
        {
            "name": "Sample for others",
            "value": 4
        },
    ]
    for option in options:
        ObservationOptions.objects.get_or_create(name=option['name'], value=option['value'])
