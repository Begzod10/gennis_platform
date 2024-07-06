from django.db import models

from branch.models import Branch
from language.models import Language
from students.models import Student
from subjects.models import Subject, SubjectLevel
from system.models import System
from teachers.models import Teacher


# Create your models here.


class Group(models.Model):
    name = models.CharField()
    price = models.IntegerField()
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    level = models.ForeignKey(SubjectLevel, on_delete=models.CASCADE)
    students = models.ManyToManyField(Student)
    teacher = models.ManyToManyField(Teacher)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    color = models.CharField()
    status = models.BooleanField()
    created_date = models.DateTimeField(auto_now_add=True)
    language = models.ForeignKey(Language, on_delete=models.CASCADE)
    teacher_salary = models.IntegerField()
    deleted = models.BooleanField()
    attendance_days = models.IntegerField()
    system = models.ForeignKey(System, on_delete=models.CASCADE)


class StudentHistoryGroups(models.Model):
    student = models.ForeignKey(Student, on_delete=models.SET_NULL, null=True)
    group = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True)
    teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True)
    reason = models.CharField(max_length=50)
    joined_day = models.DateTimeField()
    left_day = models.DateTimeField()
