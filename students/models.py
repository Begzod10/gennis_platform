from django.db import models

from subjects.models import Subject
from user.serializers import *


class Student(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE,related_name='student_user')
    subject = models.ForeignKey(Subject, on_delete=models.SET_NULL,null=True)
    total_payment_month = models.IntegerField()
    shift = models.CharField(max_length=50)
    debt_status = models.BigIntegerField()
