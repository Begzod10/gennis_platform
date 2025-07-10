from django.db import models
from user.models import CustomUser
from branch.models import Branch
from subjects.models import Subject


class LeadBlock(models.Model):
    name = models.CharField(max_length=250)
    branch = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True)
    deleted = models.BooleanField(default=False)


class Lead(models.Model):
    name = models.CharField(max_length=250)
    phone = models.CharField(max_length=250)
    surname = models.CharField(max_length=250, null=True)
    created = models.DateField(auto_now_add=True, null=True)
    branch = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True)
    type = models.CharField(max_length=250, null=True)
    deleted = models.BooleanField(default=False)
    block_id = models.ForeignKey(LeadBlock, on_delete=models.SET_NULL, null=True)
    index = models.IntegerField(null=True, blank=True, default=0)


class LeadCall(models.Model):
    lead = models.ForeignKey(Lead, related_name='lead_id_leadCall', on_delete=models.CASCADE)
    status = models.BooleanField(default=False)
    created = models.DateField(auto_now_add=True)
    delay = models.DateField(null=True)
    comment = models.TextField(null=True)
    branch = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True)
    deleted = models.BooleanField(default=False)
    audio_file = models.FileField(null=True, blank=True, upload_to='audio/', default="")
    other_infos = models.JSONField(null=True)


class OperatorPercent(models.Model):
    percent = models.IntegerField()
    total_lead = models.IntegerField()
    accepted = models.IntegerField()
    date = models.DateField(null=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
