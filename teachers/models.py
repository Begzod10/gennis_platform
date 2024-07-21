from django.conf import settings
from django.db import models

from branch.models import Branch
from payments.models import PaymentTypes
from subjects.models import Subject


class Teacher(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='teacher_user')
    subject = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True)
    color = models.CharField(max_length=50)
    total_students = models.IntegerField()
    # premium_rate = models.IntegerField()
    # class_type =models.IntegerField()


class TeacherSalary(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, related_name='teacher_id_salary')
    month_date = models.DateTimeField(null=True)
    total_salary = models.IntegerField(blank=True, null=True)
    remaining_salary = models.IntegerField(blank=True, null=True)
    taken_salary = models.IntegerField(blank=True, null=True)
    total_black_salary = models.IntegerField(blank=True, null=True)
    branch = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True, related_name='branch_id_salary')

    class Meta:
        ordering = ['id']


class TeacherBlackSalary(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, related_name='teacher_black_salary')
    black_salary = models.IntegerField(null=True)
    group = models.ForeignKey('group.Group', on_delete=models.CASCADE)
    student = models.ForeignKey('students.Student', on_delete=models.CASCADE)
    month_date = models.DateTimeField()
    status = models.BooleanField()


class TeacherSalaryList(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, related_name='teacher_id_salary_list')
    salary_id = models.ForeignKey(TeacherSalary, on_delete=models.SET_NULL, null=True,
                                  related_name='salary_id_salary_list')
    payment = models.ForeignKey(PaymentTypes, on_delete=models.SET_NULL, null=True,
                                related_name='payment_id_salary_list')
    date = models.DateTimeField(auto_now_add=True)
    comment = models.CharField(max_length=300)
    branch = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True, related_name='branch_id_salary_list')
    deleted = models.BooleanField(default='false')
    salary = models.IntegerField()

    class Meta:
        ordering = ['id']


class TeacherGroupStatistics(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True,
                                related_name='teacher_id_teacher_group_statistics')
    reason = models.ForeignKey('group.GroupReason', on_delete=models.SET_NULL, null=True,
                               related_name='group_reason_id_teacher_group_statistics')
    branch = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True,
                               related_name='branch_id_teacher_group_statistics')
    number_students = models.IntegerField()
    percentage = models.IntegerField()

    class Meta:
        ordering = ['id']
