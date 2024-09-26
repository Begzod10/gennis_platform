from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers

from subjects.models import Subject, SubjectLevel


class SubjectSerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=250, required=False)
    desc = serializers.CharField(allow_null=True, allow_blank=True, required=False)
    disabled = serializers.BooleanField(default=False, required=False)
    id = serializers.IntegerField(required=False)
    data = serializers.JSONField(required=False, write_only=True)

    class Meta:
        model = Subject
        fields = '__all__'

    def create(self, validated_data):
        subjects = []
        subject_ids = []
        for data in validated_data['data']:
            try:
                subject = Subject.objects.get(classroom_id=data['id'])
                subject.name = data['name']
                subject.desc = data.get('desc', subject.desc)
                subject.disabled = data.get('disabled', subject.disabled)
                subject.save()
                subject_ids.append(subject.id)
            except ObjectDoesNotExist:
                subject = Subject.objects.create(
                    name=data['name'],
                    desc=data.get('desc', ''),
                    disabled=data.get('disabled', False),
                    classroom_id=data['id']
                )
            subjects.append(subject)
            subject_ids.append(subject.id)

        Subject.objects.exclude(id__in=subject_ids).filter(teacher=None, student=None, group=None).delete()

        return subjects


class SubjectLevelSerializer(serializers.ModelSerializer):
    old_id = serializers.IntegerField(required=False)
    subject = serializers.PrimaryKeyRelatedField(queryset=Subject.objects.all(), required=False)
    data = serializers.JSONField(required=False, write_only=True)
    name = serializers.CharField(max_length=250, required=False)
    classroom_id = serializers.IntegerField(required=False)
    disabled = serializers.BooleanField(default=False, required=False)

    class Meta:
        model = SubjectLevel
        fields = '__all__'

    def create(self, validated_data):
        levels = []
        for data in validated_data['data']:
            try:
                level = SubjectLevel.objects.get(classroom_id=data['id'])
                level.name = data['name']
                level.desc = data['desc']
                level.subject = Subject.objects.get(classroom_id=data['subject']['id'])
                level.disabled = data.get('disabled', level.disabled)
                level.save()
            except ObjectDoesNotExist:
                level = SubjectLevel.objects.create(
                    name=data['name'],
                    subject=Subject.objects.get(classroom_id=data['subject']['id']),
                    disabled=data.get('disabled', False),
                    desc=data.get('desc', ''),
                    classroom_id=data['id']
                )
            levels.append(level)

        return levels


class SubjectLevelListSerializer(serializers.ModelSerializer):
    old_id = serializers.IntegerField(required=False)
    subject = SubjectSerializer(read_only=True)

    class Meta:
        model = SubjectLevel
        fields = '__all__'
