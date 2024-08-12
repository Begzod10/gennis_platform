from django.conf import settings
from django.db import models

from payments.models import PaymentTypes
from subjects.models import Subject
from teachers.models import Teacher
from user.serializers import (CustomUser)


class Student(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='student_user')
    subject = models.ManyToManyField(Subject, blank=True)
    total_payment_month = models.IntegerField(null=True)
    extra_payment = models.CharField(null=True)
    shift = models.CharField(max_length=50, null=True)
    debt_status = models.BigIntegerField(null=True)
    parents_number = models.CharField(max_length=250, null=True)
    representative_name = models.CharField(null=True)
    representative_surname = models.CharField(null=True)
    old_id = models.IntegerField(null=True, unique=True)
    old_money = models.BigIntegerField(null=True)


class StudentCharity(models.Model):
    charity_sum = models.IntegerField()
    group = models.ForeignKey('group.Group', on_delete=models.SET_NULL, null=True, related_name='group_id_charity')
    added_data = models.DateTimeField(auto_now_add=True)
    student = models.ForeignKey(Student, on_delete=models.SET_NULL, null=True, related_name='charity_student_id')
    old_id = models.IntegerField(null=True)
    branch = models.ForeignKey('branch.Branch', on_delete=models.SET_NULL, null=True)


class StudentPayment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.SET_NULL, null=True)
    payment_type = models.ForeignKey(PaymentTypes, on_delete=models.SET_NULL, null=True)
    payment_sum = models.IntegerField()
    added_data = models.DateTimeField(auto_now_add=True)
    status = models.BooleanField()
    deleted = models.BooleanField(default=False)


class DeletedNewStudent(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='deleted_student_student_new')
    created = models.DateTimeField(auto_now_add=True)
    comment = models.CharField(null=True)


class StudentHistoryGroups(models.Model):
    student = models.ForeignKey(Student, on_delete=models.SET_NULL, null=True, related_name='student_student_history')
    group = models.ForeignKey('group.Group', on_delete=models.SET_NULL, null=True, related_name='group_student_history')
    teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, related_name='teacher_student_history')
    reason = models.CharField(max_length=50)
    joined_day = models.DateTimeField()
    left_day = models.DateTimeField()
    old_id = models.IntegerField(null=True)


class DeletedStudent(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='deleted_student_student', null=True)
    group = models.ForeignKey('group.Group', on_delete=models.CASCADE, related_name='deleted_student_group', null=True)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='deleted_student_teacher', null=True)
    group_reason = models.ForeignKey('group.GroupReason', on_delete=models.SET_NULL, null=True,
                                     related_name='deleted_student_group_reason')
    deleted_date = models.DateTimeField(auto_now_add=True)


class ContractStudent(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='contract_student_id')
    created_date = models.DateField(auto_now_add=True)
    expire_date = models.DateField()
    father_name = models.CharField(max_length=255)
    given_place = models.CharField(max_length=255)
    place = models.CharField(max_length=255)
    passport_series = models.CharField(max_length=255)
    given_time = models.CharField(max_length=255)
    contract = models.FileField(upload_to='contracts')
    year = models.DateField(null=True)  # Add this field
