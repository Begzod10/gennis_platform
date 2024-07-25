from django.db import models

from branch.models import Branch
from language.models import Language
from students.models import Student
from subjects.models import Subject, SubjectLevel
from system.models import System
from teachers.models import Teacher


class Group(models.Model):
    name = models.CharField(max_length=255)
    price = models.IntegerField(null=True)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, null=True)
    level = models.ForeignKey(SubjectLevel, on_delete=models.CASCADE, null=True)
    students = models.ManyToManyField(Student, related_name='groups_student')
    teacher = models.ManyToManyField(Teacher)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, null=True)
    color = models.ForeignKey('class_.ClassColors', on_delete=models.CASCADE, null=True)
    status = models.BooleanField(null=True)
    created_date = models.DateTimeField(auto_now_add=True, null=True)
    language = models.ForeignKey(Language, on_delete=models.CASCADE, null=True)
    teacher_salary = models.IntegerField(null=True)
    deleted = models.BooleanField(null=True, default=False)
    attendance_days = models.IntegerField(null=True)
    system = models.ForeignKey(System, on_delete=models.CASCADE, null=True)
    class_number = models.ForeignKey('class_.ClassNumber', on_delete=models.CASCADE, null=True)

class GroupReason(models.Model):
    name = models.CharField(max_length=255)


class AttendancePerMonth(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='attendance_per_month')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='attendance_per_month')
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='attendance_per_month')
    date = models.DateTimeField()
    status = models.IntegerField()
    total_debt = models.IntegerField()
    total_salary = models.IntegerField()
    ball_percentage = models.IntegerField()
    month_date = models.DateTimeField()
    total_charity = models.IntegerField()
    remaining_debt = models.IntegerField()
    payment = models.IntegerField()
    remaining_salary = models.IntegerField()
    taken_salary = models.IntegerField()


class AttendancePerDay(models.Model):
    attendance_per_month = models.ForeignKey(AttendancePerMonth, on_delete=models.CASCADE,
                                             related_name='attendance_per_day')
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
