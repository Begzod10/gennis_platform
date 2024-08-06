from rest_framework import serializers

from teachers.models import (Teacher, Subject)
from user.serializers import CustomUser


class TeacherSerializerTransfer(serializers.ModelSerializer):
    subject = serializers.PrimaryKeyRelatedField(queryset=Subject.objects.all())

    class Meta:
        model = Teacher
        fields = ['user', 'subject', 'color', 'total_students']

    def create(self, validated_data):
        user_data = validated_data.get('user')
        subject_data = validated_data.get('subject')

        user = CustomUser.objects.get(CustomUser.old_id == user_data)

        teacher = Teacher.objects.create(user=user, **validated_data)
        for subject in subject_data:
            subject = Subject.objects.get(Subject.old_id == subject)
            teacher.subject.set(subject)

        return teacher
