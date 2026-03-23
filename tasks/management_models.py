"""
Read/write Django model mapped to the management app's mission table.
managed=False — Django will never create or migrate this table.
Always query with .using('management').
"""
from django.db import models


class ManagementMission(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    category = models.CharField(max_length=50)
    status = models.CharField(max_length=30)
    deadline = models.DateField()
    finish_date = models.DateField(null=True, blank=True)
    delay_days = models.IntegerField(default=0)
    final_sc = models.IntegerField(default=0)
    kpi_weight = models.IntegerField(default=10)
    penalty_per_day = models.IntegerField(default=2)
    early_bonus_per_day = models.IntegerField(default=1)
    max_bonus = models.IntegerField(default=3)
    max_penalty = models.IntegerField(default=10)
    deleted = models.BooleanField(default=False)

    class Meta:
        managed = False
        db_table = "mission"
        app_label = "tasks"


class ManagementMissionComment(models.Model):
    mission_id = models.BigIntegerField()
    user_id = models.BigIntegerField(null=True, blank=True)
    text = models.TextField()
    attachment = models.CharField(max_length=500, null=True, blank=True)
    creator_name = models.CharField(max_length=255, null=True, blank=True)
    deleted = models.BooleanField(default=False)

    class Meta:
        managed = False
        db_table = "mission_comment"
        app_label = "tasks"


class ManagementMissionAttachment(models.Model):
    mission_id = models.BigIntegerField()
    file = models.CharField(max_length=500)
    note = models.CharField(max_length=255, null=True, blank=True)
    creator_name = models.CharField(max_length=255, null=True, blank=True)
    deleted = models.BooleanField(default=False)

    class Meta:
        managed = False
        db_table = "mission_attachment"
        app_label = "tasks"


class ManagementMissionProof(models.Model):
    mission_id = models.BigIntegerField()
    file = models.CharField(max_length=500)
    comment = models.CharField(max_length=255, null=True, blank=True)
    creator_name = models.CharField(max_length=255, null=True, blank=True)
    deleted = models.BooleanField(default=False)

    class Meta:
        managed = False
        db_table = "mission_proof"
        app_label = "tasks"
