from rest_framework import serializers

from .models import Lead, LeadCall


class LeadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lead
        fields = ['id', 'name', 'phone', 'subject', 'branch']


class LeadCallSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeadCall
        fields = ['id', 'lead', 'delay', 'comment']
