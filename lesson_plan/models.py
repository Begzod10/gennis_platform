from django.db import models

from group.models import Group
from school_time_table.models import Hours
from students.models import Student
from teachers.models import Teacher
from flows.models import Flow


class LessonPlan(models.Model):
    group = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True)
    flow = models.ForeignKey(Flow, on_delete=models.SET_NULL, null=True)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    date = models.DateField()
    objective = models.TextField(null=True, blank=True)
    main_lesson = models.TextField(null=True, blank=True)
    homework = models.TextField(null=True, blank=True)
    assessment = models.TextField(null=True, blank=True)
    activities = models.TextField(null=True, blank=True)
    resources = models.TextField(null=True, blank=True)
    updated = models.DateField(null=True)
    ball = models.PositiveSmallIntegerField(null=True, blank=True)
    conclusion = models.TextField(null=True, blank=True)
    subject =models.ForeignKey('subjects.Subject', on_delete=models.SET_NULL, null=True)
    hour_id =models.ForeignKey(Hours,on_delete=models.SET_NULL, null=True)


    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['group', 'flow', 'teacher', 'date','subject','hour_id'],
                name='unique_lesson_plan'
            )
        ]


class LessonPlanStudents(models.Model):
    lesson_plan = models.ForeignKey(LessonPlan, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    comment = models.TextField()


class LessonPlanFile(models.Model):
    class Status(models.TextChoices):
        PENDING   = 'pending',   'Kutilmoqda'
        CHECKING  = 'checking',  'Tekshirilmoqda'
        DONE      = 'done',      'Baholandi'
        FAILED    = 'failed',    'Xatolik'

    teacher   = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='lesson_plan_files')
    term      = models.ForeignKey('terms.Term', on_delete=models.CASCADE, related_name='lesson_plan_files')
    file      = models.FileField(upload_to='lesson_plan_files/%Y/%m/')
    status    = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    score     = models.PositiveSmallIntegerField(null=True, blank=True)   # 0-100
    rating    = models.PositiveSmallIntegerField(null=True, blank=True)  # 0-5 manual rating
    feedback  = models.TextField(null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-uploaded_at']
        unique_together = ['teacher', 'term']
