from django.db import models

from students.models import Student
from teachers.models import Teacher
from group.models import Group


class AttendancePerMonth(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='attendance_per_month')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='attendance_per_month')
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='attendance_per_month')
    status = models.IntegerField(default=False)
    total_debt = models.IntegerField(default=0)
    total_salary = models.IntegerField(default=0)
    ball_percentage = models.IntegerField(default=0)
    month_date = models.DateTimeField()
    total_charity = models.IntegerField(default=0)
    remaining_debt = models.IntegerField(default=0)
    payment = models.IntegerField(default=0)
    remaining_salary = models.IntegerField(default=0)
    taken_salary = models.IntegerField(default=0)


class AttendancePerDay(models.Model):
    attendance_per_month = models.ForeignKey(AttendancePerMonth, on_delete=models.CASCADE)
    debt_per_day = models.IntegerField()
    salary_per_day = models.IntegerField()
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='attendance_per_day')
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='attendance_per_day')
    charity_per_day = models.IntegerField()
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='attendance_per_day')
    day = models.DateTimeField()
    homework_ball = models.IntegerField()
    dictionary_ball = models.IntegerField()
    activeness_ball = models.IntegerField()
    average = models.IntegerField()
    status = models.IntegerField()
