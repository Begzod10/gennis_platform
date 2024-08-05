from rest_framework import serializers

from subjects.models import Subject, SubjectLevel


class SubjectSerializer(serializers.ModelSerializer):
    old_id = serializers.IntegerField(required=False)

    class Meta:
        model = Subject
        fields = ['id', 'name', 'ball_number', 'old_id']


class SubjectLevelSerializer(serializers.ModelSerializer):
    old_id = serializers.IntegerField(required=False)
    subject = serializers.PrimaryKeyRelatedField(queryset=Subject.objects.all())

    class Meta:
        model = SubjectLevel
        fields = '__all__'


class SubjectLevelListSerializer(serializers.ModelSerializer):
    old_id = serializers.IntegerField(required=False)
    subject = SubjectSerializer(read_only=True)

    class Meta:
        model = SubjectLevel
        fields = '__all__'
