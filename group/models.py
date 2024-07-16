from django.db import models
from branch.models import Branch
from language.models import Language
from students.models import Student
from subjects.models import Subject, SubjectLevel
from system.models import System
from teachers.models import Teacher


class Group(models.Model):
    name = models.CharField(max_length=100)  # Specify max_length
    price = models.IntegerField()
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    level = models.ForeignKey(SubjectLevel, on_delete=models.CASCADE)
    students = models.ManyToManyField(Student)
    teacher = models.ManyToManyField(Teacher)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    color = models.CharField(max_length=50)  # Specify max_length
    status = models.BooleanField()
    created_date = models.DateTimeField(auto_now_add=True)
    language = models.ForeignKey(Language, on_delete=models.CASCADE)
    teacher_salary = models.IntegerField()
    deleted = models.BooleanField()
    attendance_days = models.IntegerField()
    system = models.ForeignKey(System, on_delete=models.CASCADE)


class GroupReason(models.Model):
    name = models.CharField(max_length=100)  # Specify max_length


class AttendancePerMonth(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='attendance_per_months')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='attendance_per_months')
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='attendance_per_months')
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
                                             related_name='attendance_per_days')
    debt_per_day = models.IntegerField()
    salary_per_day = models.IntegerField()
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='attendance_per_days')
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='attendance_per_days')
    charity_per_day = models.IntegerField()
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='attendance_per_days')
    day = models.DateTimeField()
    homework_ball = models.IntegerField()
    dictionary_ball = models.IntegerField()
    activeness_ball = models.IntegerField()
    average = models.IntegerField()
    status = models.IntegerField()
