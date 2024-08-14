from rest_framework import serializers

from branch.models import Branch
from subjects.serializers import Subject
from teachers.models import Teacher
from user.serializers import CustomUser
from students.models import Student, StudentHistoryGroups, StudentCharity
from django.db import transaction
from group.models import Group


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


class StudentHistoryGroupCreateSerializer(serializers.ModelSerializer):
    student = serializers.SlugRelatedField(queryset=Student.objects.all(), slug_field='old_id')
    group = serializers.SlugRelatedField(queryset=Group.objects.all(), slug_field='old_id')
    teacher = serializers.SlugRelatedField(queryset=Teacher.objects.all(), slug_field='old_id')

    class Meta:
        model = StudentHistoryGroups
        fields = ['id', 'student', 'group', 'teacher', 'reason', 'joined_day', 'left_day', 'old_id']


class TransferStudentCharitySerializer(serializers.ModelSerializer):
    student = serializers.SlugRelatedField(queryset=StudentHistoryGroups.objects.all(), slug_field='old_id')
    group = serializers.SlugRelatedField(queryset=Group.objects.all(), slug_field='old_id')
    branch = serializers.SlugRelatedField(queryset=Branch.objects.all(), slug_field='old_id')

    class Meta:
        model = StudentCharity
        fields = ['id', 'charity_sum', 'added_data', 'student', 'old_id', 'branch', 'group']
