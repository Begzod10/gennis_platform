from django.contrib.auth.models import Group
from django.db import models

from branch.models import Branch
from students.models import Student


class Task(models.Model):
    name = models.CharField()
    auth_group = models.ForeignKey(Group, related_name='auth_group_task')
    branch = models.ForeignKey(Branch, related_name='branch_id_task')


class StudentCallInfo(models.Model):
    student = models.ForeignKey(Student, related_name='student_call_info')
