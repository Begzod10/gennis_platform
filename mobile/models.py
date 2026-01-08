from django.db import models

from teachers.models import Teacher


# Create your models here.
class TeacherDashboard(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    attendance_percentage = models.FloatField(default=0)
    task_count = models.IntegerField(default=0)
    rank = models.IntegerField(default=0)
    class_count = models.IntegerField(default=0)
    task_completed = models.BooleanField(default=False)
    lessons_count = models.IntegerField(default=0)
