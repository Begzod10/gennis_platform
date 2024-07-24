from rest_framework import serializers

from branch.models import Branch
from subjects.models import Subject
from .models import Lead, LeadCall


class LeadSerializer(serializers.ModelSerializer):
    subject = serializers.PrimaryKeyRelatedField(queryset=Subject.objects.all())
    branch = serializers.PrimaryKeyRelatedField(queryset=Branch.objects.all())

    class Meta:
        model = Lead
        fields = ['id', 'name', 'phone', 'subject', 'branch']


class LeadCallSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeadCall
        fields = ['id', 'lead', 'delay', 'comment']
