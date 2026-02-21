from django.db import models

from user.models import CustomUser


class Parent(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    children = models.ManyToManyField('students.Student')
