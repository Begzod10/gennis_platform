from django.conf import settings
from django.contrib.auth.models import Group
from django.db import models

from branch.models import Branch
from students.models import Student


class Task(models.Model):
    name = models.CharField()
    auth_group = models.ForeignKey(Group, related_name='auth_group_task', on_delete=models.CASCADE)
    branch = models.ForeignKey(Branch, related_name='branch_id_task', on_delete=models.CASCADE)


class StudentCallInfo(models.Model):
    student = models.ForeignKey(Student, related_name='student_call_info', on_delete=models.CASCADE)
    task = models.ForeignKey(Task, related_name='task_call_info', on_delete=models.CASCADE)
    created = models.DateField(auto_now_add=True)
    delay_date = models.DateField()
    comment = models.CharField()
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='user_call_info', on_delete=models.CASCADE)
    student_tasks = models.ForeignKey('TaskStudent', related_name='student_task', on_delete=models.CASCADE)


class TaskStatistics(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='user_static_info', on_delete=models.CASCADE)
    task = models.ForeignKey(Task, related_name='task_static_info', on_delete=models.CASCADE)
    completed_num = models.IntegerField()
    progress_num = models.IntegerField()
    percentage = models.IntegerField()
    day = models.DateField()


class TaskDailyStatistics(models.Model):
    day = models.DateField()
    completed_num = models.IntegerField()
    progress_num = models.IntegerField()
    percentage = models.IntegerField()
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='user_static_day', on_delete=models.CASCADE)


class TaskStudent(models.Model):
    task = models.ForeignKey(Task, related_name='task_static_student', on_delete=models.CASCADE)
    task_static = models.ForeignKey(TaskStatistics, related_name='task_static_student_info', on_delete=models.CASCADE)
    status = models.BooleanField()
    students = models.ForeignKey(Student, related_name='task_student_isd', on_delete=models.CASCADE)
