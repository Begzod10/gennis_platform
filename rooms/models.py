from django.db import models

from branch.models import Branch
from subjects.models import Subject


class Room(models.Model):
    name = models.CharField(max_length=250)
    seats_number = models.BigIntegerField()
    branch = models.ForeignKey(Branch, related_name='branch_id', on_delete=models.SET_NULL, null=True)
    electronic_board = models.BooleanField()
    deleted = models.BooleanField(default=False)
    old_id = models.IntegerField(null=True, unique=True)
    # turon_old_id = models.IntegerField(null=True, unique=True)


class RoomImages(models.Model):
    image = models.ImageField(upload_to='room_images')
    room = models.ForeignKey(Room, related_name='room_id', on_delete=models.SET_NULL, null=True)
    old_id = models.IntegerField(null=True, unique=True)


class RoomSubject(models.Model):
    subject = models.ForeignKey(Subject, related_name='subject_id_room', on_delete=models.SET_NULL, null=True)
    room = models.ForeignKey(Room, related_name='room_id_for_room_subject', on_delete=models.SET_NULL, null=True)
