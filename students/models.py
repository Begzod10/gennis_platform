from django.db import models
from django.conf import settings
from subjects.models import Subject
from payments.models import PaymentTypes
from teachers.models import Teacher
from user.serializers import (CustomUser)


class Student(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='student_user')
    subject = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True)
    total_payment_month = models.IntegerField(null=True)
    shift = models.CharField(max_length=50, null=True)
    debt_status = models.BigIntegerField(null=True)
    parents_number = models.CharField(max_length=250, null=True)


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


class DeletedStudent(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='deleted_student_student')
    created = models.DateTimeField(auto_now_add=True)


class StudentHistoryGroups(models.Model):
    student = models.ForeignKey(Student, on_delete=models.SET_NULL, null=True, related_name='student_student_history')
    group = models.ForeignKey('group.Group', on_delete=models.SET_NULL, null=True, related_name='group_student_history')
    teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, related_name='teacher_student_history')
    reason = models.CharField(max_length=50)
    joined_day = models.DateTimeField()
    left_day = models.DateTimeField()


class DeletedStudent(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='deleted_student_student')
    group = models.ForeignKey('group.Group', on_delete=models.CASCADE, related_name='deleted_student_group')
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='deleted_student_teacher')
    group_reason = models.ForeignKey('group.GroupReason', on_delete=models.SET_NULL, null=True,
                                     related_name='deleted_student_group_reason')
    deleted_date = models.DateTimeField(auto_now_add=True)
