from django.db import models


# Create your models here.


class FlowTypes(models.Model):
    name = models.CharField()
    classes = models.JSONField()
    color = models.CharField()


class Flow(models.Model):
    name = models.CharField()
    flow_type = models.ForeignKey(FlowTypes, on_delete=models.CASCADE)
    subject = models.ForeignKey('subjects.Subject', on_delete=models.CASCADE)
    teacher = models.ForeignKey('teachers.Teacher', on_delete=models.CASCADE)
    students = models.ManyToManyField('students.Student')
    activity = models.BooleanField(default=False)
    level = models.ForeignKey('subjects.SubjectLevel', on_delete=models.CASCADE, null=True)
