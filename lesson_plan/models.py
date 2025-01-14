from django.db import models

from group.models import Group
from teachers.models import Teacher
from students.models import Student

class LessonPlan(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    date = models.DateField()
    objective = models.TextField(null=True, blank=True)
    main_lesson = models.TextField(null=True, blank=True)
    homework = models.TextField(null=True, blank=True)
    assessment = models.TextField(null=True, blank=True)
    activities = models.TextField(null=True, blank=True)
    resources = models.TextField(null=True, blank=True)
    updated = models.DateField(null=True)


class LessonPlanStudents(models.Model):
    lesson_plan = models.ForeignKey(LessonPlan, on_delete=models.CASCADE)
    student = models.ForeignKey(Student,on_delete=models.CASCADE)
    comment = models.TextField()
