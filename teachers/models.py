from django.conf import settings
from django.db import models

from branch.models import Branch
from payments.models import PaymentTypes
from subjects.models import Subject
from system.models import System


class TeacherSalaryType(models.Model):
    name = models.CharField()
    salary = models.IntegerField()


class Teacher(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='teacher_user')
    subject = models.ManyToManyField(Subject, blank=True)
    color = models.CharField(max_length=50, null=True)
    total_students = models.IntegerField(null=True)
    premium_rate = models.IntegerField(null=True)
    class_type = models.IntegerField(null=True)
    teacher_salary_type = models.ForeignKey(TeacherSalaryType, on_delete=models.SET_NULL, null=True)
    old_id = models.IntegerField(unique=True, null=True)
    branches = models.ManyToManyField(Branch, blank=True)


class TeacherAttendance(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True,
                                related_name='teacher_attendance_teacher')
    day = models.DateTimeField(null=True)
    status = models.BooleanField(null=True)
    system = models.ForeignKey(System, on_delete=models.SET_NULL, null=True, related_name='teacher_attendance_system')

    class Meta:
        ordering = ['id']


class TeacherSalary(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, related_name='teacher_id_salary')
    month_date = models.DateField(null=True)
    total_salary = models.BigIntegerField(blank=True, null=True)
    remaining_salary = models.BigIntegerField(blank=True, null=True)
    taken_salary = models.BigIntegerField(blank=True, null=True)
    total_black_salary = models.BigIntegerField(blank=True, null=True)
    percentage = models.IntegerField(default=50)
    branch = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True, related_name='branch_id_salary')
    teacher_salary_type = models.ForeignKey(TeacherSalaryType, on_delete=models.SET_NULL, null=True)
    worked_days = models.IntegerField(null=True)
    old_id = models.IntegerField(blank=True, null=True, unique=True)

    class Meta:
        ordering = ['id']


class TeacherBlackSalary(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, related_name='teacher_black_salary')
    black_salary = models.IntegerField(null=True)
    group = models.ForeignKey('group.Group', on_delete=models.CASCADE, null=True)
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


class TeacherHistoryGroups(models.Model):
    group = models.ForeignKey('group.Group', on_delete=models.SET_NULL, null=True, related_name='group_teacher_history')
    teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, related_name='teacher_teacher_history')
    reason = models.CharField(max_length=50)
    joined_day = models.DateTimeField()
    left_day = models.DateTimeField()
