from django.db import models

from subjects.models import Subject

from user.serializers import UserSerializer, CustomUser


class Teacher(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='teacher_user')
    subject = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True)
    color = models.CharField(max_length=50)
    total_students = models.IntegerField()

# class TeacherSalary()
