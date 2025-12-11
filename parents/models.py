from django.db import models

from students.models import Student
from user.models import CustomUser


class Parent(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    children = models.ManyToManyField(Student)
