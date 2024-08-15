from django.db import models

from students.models import Student
from teachers.models import Teacher
from group.models import Group


class AttendancePerMonth(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, null=True)
    status = models.IntegerField(default=False, null=True)
    total_debt = models.IntegerField(default=0, null=True)
    total_salary = models.IntegerField(default=0, null=True)
    ball_percentage = models.IntegerField(default=0, null=True)
    month_date = models.DateTimeField(null=True)
    total_charity = models.IntegerField(default=0, null=True)
    remaining_debt = models.IntegerField(default=0, null=True)
    payment = models.IntegerField(default=0)
    system = models.ForeignKey('system.System', on_delete=models.CASCADE, null=True)
    old_id = models.IntegerField(null=True, unique=True)
    remaining_salary = models.IntegerField(default=0, null=True)
    taken_salary = models.IntegerField(default=0, null=True)
    present_days = models.IntegerField(default=0, null=True)
    absent_days = models.IntegerField(default=0, null=True)
    scored_days = models.IntegerField(default=0, null=True)


class AttendancePerDay(models.Model):
    attendance_per_month = models.ForeignKey(AttendancePerMonth, on_delete=models.CASCADE, null=True)
    debt_per_day = models.IntegerField(null=True)
    salary_per_day = models.IntegerField(null=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, null=True)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, null=True)
    charity_per_day = models.IntegerField(null=True)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, null=True)
    day = models.DateTimeField(null=True)
    homework_ball = models.IntegerField(null=True)
    dictionary_ball = models.IntegerField(null=True)
    activeness_ball = models.IntegerField(null=True)
    average = models.IntegerField(null=True)
    status = models.BooleanField(default=False)
    old_id = models.IntegerField(null=True, unique=True)
    reason = models.CharField(null=True)
    teacher_ball = models.IntegerField(null=True)


class GroupAttendancesPerMonth(models.Model):
    total_debt = models.IntegerField(null=True)
    total_salary = models.IntegerField(null=True)
    month_date = models.DateTimeField(null=True)
    total_charity = models.IntegerField(null=True)
    remaining_debt = models.IntegerField(null=True)
    payment = models.IntegerField(null=True)
    remaining_salary = models.IntegerField(null=True)
    taken_salary = models.IntegerField(null=True)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
