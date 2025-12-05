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


class Category(models.TextChoices):
    ACADEMIC = "academic", "Academic"
    ADMIN = "admin", "Admin"
    STUDENT = "student", "Student-related"
    REPORT = "report", "Report"
    MEETING = "meeting", "Meeting/Event"
    MARKETING = "marketing", "Marketing"
    MAINTENANCE = "maintenance", "Maintenance"
    FINANCE = "finance", "Finance"


class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Mission(models.Model):
    STATUS_CHOICES = (
        ("not_started", "Not Started"),
        ("in_progress", "In Progress"),
        ("blocked", "Blocked"),
        ("completed", "Completed"),
        ("approved", "Approved"),
        ("declined", "Declined"),
        ("recheck", "Re-check"),
    )

    title = models.CharField(max_length=255)
    final_sc = models.IntegerField(default=0)

    description = models.TextField(blank=True, null=True)

    category = models.CharField(max_length=50, choices=Category.choices, default=Category.ACADEMIC)
    tags = models.ManyToManyField(Tag, blank=True, related_name="missions")

    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="created_missions")
    executor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="executed_missions")
    reviewer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name="reviewed_missions")

    branch = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True, blank=True)

    # Date only fields (faqat yil-oy-kun). Agar sizga time ham kerak bo'lsa DateTimeField ga o'zgartiring.
    start_date = models.DateField(auto_now_add=True)
    deadline = models.DateField()
    finish_date = models.DateField(null=True, blank=True)

    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default="not_started")

    # KPI and penalty
    kpi_weight = models.IntegerField(default=10)
    penalty_per_day = models.IntegerField(default=2)  # penalty integer per day
    early_bonus_per_day = models.IntegerField(default=1)
    max_bonus = models.IntegerField(default=3)
    max_penalty = models.IntegerField(default=10)

    # delay kun bo'yicha
    delay_days = models.IntegerField(default=0)

    # recurring
    is_recurring = models.BooleanField(default=False)
    recurring_type = models.CharField(
        max_length=20,
        choices=[
            ("daily", "Daily"),
            ("weekly", "Weekly"),
            ("monthly", "Monthly"),
            ("custom", "Custom"),
        ],
        null=True,
        blank=True
    )
    repeat_every = models.IntegerField(default=1)  # kunlarda
    last_generated = models.DateField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    def calculate_delay_days(self):
        if self.finish_date and self.deadline:
            self.delay_days = (self.finish_date - self.deadline).days
        else:
            self.delay_days = 0
        return self.delay_days

    def final_score(self):
        delay = self.delay_days
        base = self.kpi_weight

        # ❗ Agar erta tugatgan bo‘lsa — BONUS
        if delay < 0:
            bonus = abs(delay) * self.early_bonus_per_day
            bonus = min(bonus, self.max_bonus)  # limit
            return base + bonus

        # ❗ Agar vaqtida tugatgan bo‘lsa — to‘liq kpi_weight
        if delay == 0:
            return base

        # ❗ Agar kechiktirgan bo‘lsa — PENALTY
        penalty = delay * self.penalty_per_day
        penalty = min(penalty, self.max_penalty)  # limit

        score = base - penalty
        return max(0, score)  # ball minus bo‘lmasin


class MissionSubtask(models.Model):
    mission = models.ForeignKey(Mission, on_delete=models.CASCADE, related_name="subtasks")
    title = models.CharField(max_length=255)
    is_done = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]


class MissionAttachment(models.Model):
    mission = models.ForeignKey(Mission, on_delete=models.CASCADE, related_name="attachments")
    file = models.FileField(upload_to="mission_attachments/")
    uploaded_at = models.DateTimeField(auto_now_add=True)
    note = models.CharField(max_length=255, null=True, blank=True)


class MissionComment(models.Model):
    mission = models.ForeignKey(Mission, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    text = models.TextField()
    attachment = models.FileField(upload_to="mission_comments/", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class MissionProof(models.Model):
    mission = models.ForeignKey(Mission, on_delete=models.CASCADE, related_name="proofs")
    file = models.FileField(upload_to="mission_proofs/")
    comment = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    mission = models.ForeignKey(Mission, on_delete=models.CASCADE, null=True, blank=True)
    message = models.TextField()
    role = models.CharField(max_length=20)  # executor / creator / reviewer
    deadline = models.DateField(null=True, blank=True)  # NEW
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)  # qachon yuborilgan
