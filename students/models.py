from django.db import models
from django.conf import settings
from subjects.models import Subject
from payments.models import PaymentTypes
from user.serializers import (CustomUser)


class Student(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='student_user')
    subject = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True)
    total_payment_month = models.IntegerField()
    shift = models.CharField(max_length=50)
    debt_status = models.BigIntegerField()


class StudentCharity(models.Model):
    charity_sum = models.IntegerField()
    group = models.ForeignKey('group.Group', on_delete=models.SET_NULL, null=True, related_name='group_id_charity')
    added_data = models.DateTimeField(auto_now_add=True)
    student = models.ForeignKey(Student, on_delete=models.SET_NULL, null=True, related_name='charity_student_id')


class StudentPayment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.SET_NULL, null=True)
    payment_type = models.ForeignKey(PaymentTypes, on_delete=models.SET_NULL, null=True)
    payment_sum = models.IntegerField()
    added_data = models.DateTimeField(auto_now_add=True)
    status = models.BooleanField()
