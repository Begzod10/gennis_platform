from rest_framework import serializers

from branch.models import Branch
from branch.serializers import BranchSerializer
from subjects.models import Subject
from subjects.serializers import SubjectSerializer
from .models import Lead, LeadCall


class LeadSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    name = serializers.CharField(max_length=255, required=False)
    phone = serializers.CharField(max_length=255, required=False)
    subject = serializers.PrimaryKeyRelatedField(queryset=Subject.objects.all())
    branch = serializers.PrimaryKeyRelatedField(queryset=Branch.objects.all())

    class Meta:
        model = Lead
        fields = ['id', 'name', 'phone', 'subject', 'branch']

    def create(self, validated_data):
        subject_data = validated_data.pop('subject')
        branch_data = validated_data.pop('branch')
        subject, _ = Subject.objects.get_or_create(**subject_data)
        branch, _ = Branch.objects.get_or_create(**branch_data)

        lead = Lead.objects.create(
            subject=subject,
            branch=branch,
            **validated_data
        )
        return lead

    def update(self, instance, validated_data):
        subject_data = validated_data.pop('subject', None)
        branch_data = validated_data.pop('branch', None)
        if subject_data:
            subject, _ = Subject.objects.get_or_create(**subject_data)
            instance.subject = subject
        if branch_data:
            branch, _ = Branch.objects.get_or_create(**branch_data)
            instance.branch = branch
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


class LeadListSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    name = serializers.CharField(max_length=255, required=False)
    phone = serializers.CharField(max_length=255, required=False)
    subject = SubjectSerializer(required=False)
    branch = BranchSerializer(required=False)

    class Meta:
        model = Lead
        fields = ['id', 'name', 'phone', 'subject', 'branch']


class LeadCallSerializer(serializers.ModelSerializer):
    lead = serializers.PrimaryKeyRelatedField(queryset=Lead.objects.all())

    class Meta:
        model = LeadCall
        fields = ['id', 'lead', 'delay', 'comment']

    def create(self, validated_data):
        lead_data = validated_data.pop('lead')
        lead = Lead.objects.get_or_create(**lead_data)
        lead_call = LeadCall.objects.create(lead=lead, **validated_data)

        return lead_call

    def update(self, instance, validated_data):
        lead_data = validated_data.pop('lead', None)
        if lead_data:
            lead_serializer = LeadSerializer(instance=instance.lead, data=lead_data, partial=True)
            lead_serializer.is_valid(raise_exception=True)
            lead_serializer.save()
        instance.delay = validated_data.get('delay', instance.delay)
        instance.comment = validated_data.get('comment', instance.comment)
        instance.save()

        return instance


class LeadCallListSerializer(serializers.ModelSerializer):
    lead = LeadSerializer()

    class Meta:
        model = LeadCall
        fields = ['id', 'lead', 'delay', 'comment']
