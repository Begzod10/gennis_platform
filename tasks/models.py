from django.conf import settings
from django.contrib.auth.models import Group
from django.db import models

from branch.models import Branch
from students.models import Student
from user.models import CustomUser


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


class Mission(models.Model):
    STATUS_CHOICES = (
        ("not_started", "Not Started"),
        ("in_progress", "In Progress"),
        ("blocked", "Blocked"),
        ("completed", "Completed"),
    )

    title = models.CharField(max_length=255)
    comment = models.CharField(max_length=255, null=True)
    description = models.TextField()
    branch = models.ForeignKey(
        Branch,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="missions"
    )
    creator = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="created_workitems")
    executor = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="executed_workitems")
    reviewer = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name="reviewed_workitems")

    start_time = models.DateField(auto_now_add=True)  # faqat kun
    deadline = models.DateField()      # ✅ faqat kun
    finish_time = models.DateField(null=True, blank=True)  # ✅ faqat kun

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="not_started")

    created_at = models.DateField(auto_now_add=True)
    delay_days = models.IntegerField(default=0)

    def __str__(self):
        return self.title
