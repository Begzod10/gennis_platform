from django.db import transaction
from rest_framework import serializers

from teachers.models import (Teacher, Subject)
from user.serializers import CustomUser


class TeacherSerializerTransfer(serializers.ModelSerializer):
    subject = serializers.SlugRelatedField(queryset=Subject.objects.all(), slug_field='old_id', many=True)
    user = serializers.SlugRelatedField(queryset=CustomUser.objects.all(), slug_field='old_id')

    class Meta:
        model = Teacher
        fields = '__all__'

    @transaction.atomic
    def create(self, validated_data):
        user_data = validated_data.pop('user')
        subject_data = validated_data.pop('subject', [])

        user = CustomUser.objects.get(old_id=user_data.old_id)

        teacher = Teacher.objects.create(user=user, **validated_data)

        teacher.subject.clear()
        for subject in subject_data:
            subject_instance = Subject.objects.get(old_id=subject.old_id)
            teacher.subject.add(subject_instance)

        return teacher
