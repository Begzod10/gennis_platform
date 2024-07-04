from django.db import models

from subjects.models import Subject
from teachers.models import Teacher
from user.serializers import (CustomUser, UserSerializer)


class Student(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='student_user')
    subject = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True)
    total_payment_month = models.IntegerField()
    shift = models.CharField(max_length=50)
    debt_status = models.BigIntegerField()


class StudentHistoryGroups(models.Model):
    student = models.ForeignKey(Student, on_delete=models.SET_DEFAULT, default=None)
    # group = models.ForeignKey(Student, on_delete=models.SET_DEFAULT, default=None)
    teacher = models.ForeignKey(Teacher, on_delete=models.SET_DEFAULT, default=None)
    reason = models.CharField(max_length=50)
    joined_day = models.DateTimeField()
    left_day = models.DateTimeField()
