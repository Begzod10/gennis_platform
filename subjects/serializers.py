from rest_framework import serializers

from subjects.models import Subject, SubjectLevel


class SubjectSerializer(serializers.ModelSerializer):

    class Meta:
        model = Subject
        fields = ['id', 'name', 'ball_number']




class SubjectLevelSerializer(serializers.ModelSerializer):
    subject = SubjectSerializer(read_only=True)

    class Meta:
        model = SubjectLevel
        fields = '__all__'


