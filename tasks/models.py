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
    created = models.DateTimeField(auto_now_add=True)
    delay_date = models.DateField()
    comment = models.CharField()
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='user_call_info', on_delete=models.CASCADE)
    student_tasks = models.ManyToManyField(Task)


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
