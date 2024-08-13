from django.db import models
from branch.models import Branch
from group.models import Group
from rooms.models import Room
from students.models import Student


class WeekDays(models.Model):
    name_en = models.CharField(null=True)
    name_uz = models.CharField(null=True)
    order = models.IntegerField(null=True)


class GroupTimeTable(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='group_time_table')
    week = models.ForeignKey(WeekDays, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    start_time = models.TimeField()
    end_time = models.TimeField()
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    old_id = models.IntegerField(null=True)


class TimeTableArchive(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    week = models.ForeignKey(WeekDays, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    start_time = models.TimeField()
    end_time = models.TimeField()
    date = models.DateTimeField(auto_now_add=True)


class StudentTimTableArchive(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    archive = models.ForeignKey(TimeTableArchive, on_delete=models.CASCADE)
