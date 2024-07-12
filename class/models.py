from django.db import models
from subjects.models import Subject
from group.models import Group
from students.models import Student


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


class ClassCoin(models.Model):
    total_coin = models.IntegerField()
    given_coin = models.IntegerField()
    remaining_coin = models.IntegerField()
    month_date = models.DateField()
    group = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True)

    class Meta:
        ordering = ['id']


class CoinInfo(models.Model):
    value = models.CharField()
    reason = models.CharField()
    day_date = models.DateField()
    class_coin = models.ForeignKey(ClassCoin, on_delete=models.SET_NULL, null=True)

    class Meta:
        ordering = ['id']


class StudentCoin(models.Model):
    value = models.CharField()
    class_coin = models.ForeignKey(ClassCoin, on_delete=models.SET_NULL, null=True)
    student = models.ForeignKey(Student, on_delete=models.SET_NULL, null=True)

    class Meta:
        ordering = ['id']
