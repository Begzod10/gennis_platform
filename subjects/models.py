from django.db import models


class Subject(models.Model):
    name = models.CharField(max_length=250, blank=False, null=False)
    ball_number = models.IntegerField(null=True)
    desc = models.CharField(null=True, blank=True)
    old_id = models.IntegerField(null=True, unique=True)
    classroom_id = models.IntegerField(null=True)
    disabled = models.BooleanField(default=False)


class SubjectLevel(models.Model):
    name = models.CharField(max_length=250, blank=False, null=False)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='levels')
    old_id = models.IntegerField(null=True, unique=True)
    classroom_id = models.IntegerField(null=True)
    disabled = models.BooleanField(default=False)
