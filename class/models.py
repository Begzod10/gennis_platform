from django.db import models
from subjects.models import Subject


class ClassColors(models.Model):
    name = models.CharField()
    value = models.CharField()

    class Meta:
        ordering = ['id']


class ClassTypes(models.Model):
    name = models.CharField()

    class Meta:
        ordering = ['id']


class ClassNumber(models.Model):
    number = models.IntegerField()
    curriculum_hours = models.IntegerField()
    class_types = models.ForeignKey(ClassTypes, on_delete=models.SET_NULL, null=True)
    subjects = models.ManyToManyField(Subject)

    class Meta:
        ordering = ['id']
