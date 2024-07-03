from django.db import models


class Subject(models.Model):
    name = models.CharField(max_length=250, blank=False, null=False)
    ball_number = models.IntegerField(null=True)


class SubjectLevel(models.Model):
    name = models.CharField(max_length=250, blank=False, null=False)
    subject_id = models.ForeignKey(Subject, on_delete=models.CASCADE,related_name='levels')
