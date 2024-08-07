from rest_framework import serializers
from subjects.serializers import Subject
from user.serializers import CustomUser
from students.models import Student
from django.db import transaction


class StudentSerializerTransfer(serializers.ModelSerializer):
    subject = serializers.SlugRelatedField(queryset=Subject.objects.all(), slug_field='old_id', many=True)
    user = serializers.SlugRelatedField(queryset=CustomUser.objects.all(), slug_field='old_id')

    class Meta:
        model = Student
        fields = '__all__'

    @transaction.atomic
    def create(self, validated_data):
        user_data = validated_data.pop('user')
        subject_data = validated_data.pop('subject', [])

        user = CustomUser.objects.get(old_id=user_data.old_id)

        student = Student.objects.create(user=user, **validated_data)

        student.subject.clear()
        for subject in subject_data:
            subject_instance = Subject.objects.get(old_id=subject.old_id)
            student.subject.add(subject_instance)
        return student
