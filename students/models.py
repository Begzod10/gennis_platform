from django.db import models
from django.conf import settings
from subjects.models import Subject
# from group.models import Group
# from user.models import CustomUser


class Student(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='student_user')
    subject = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True)
    total_payment_month = models.IntegerField()
    shift = models.CharField(max_length=50)
    debt_status = models.BigIntegerField()


