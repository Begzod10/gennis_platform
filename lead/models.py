from django.db import models

from branch.models import Branch
from subjects.models import Subject


class Lead(models.Model):
    name = models.CharField(max_length=250)
    phone = models.CharField(max_length=250)
    subject = models.ForeignKey(Subject, related_name='subject_id_lead', on_delete=models.CASCADE)
    branch = models.ForeignKey(Branch, related_name='branch_id_lead', on_delete=models.CASCADE)


class LeadCall(models.Model):
    lead = models.ForeignKey(Lead, related_name='lead_id_leadCall',on_delete=models.CASCADE)
    created = models.DateField(auto_now_add=True)
    delay = models.DateField()
    comment = models.TextField()
