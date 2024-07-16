from rest_framework import serializers

from subjects.models import Subject, SubjectLevel


class SubjectSerializer(serializers.ModelSerializer):

    class Meta:
        model = Subject
        fields = ['id', 'name', 'ball_number']

    def create(self, validated_data):
        return Subject.objects.create(**validated_data)


class SubjectLevelSerializer(serializers.ModelSerializer):
    subject_id = SubjectSerializer(read_only=True)

    class Meta:
        model = SubjectLevel
        fields = ['id', 'name', 'subject_id']

    def create(self, validated_data):
        return SubjectLevel.objects.create(**validated_data)
