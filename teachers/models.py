from django.db import models
from django.conf import settings
from subjects.models import Subject


class Teacher(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='teacher_user')
    subject = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True)
    color = models.CharField(max_length=50)
    total_students = models.IntegerField()
