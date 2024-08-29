from students.models import DeletedNewStudent
from students.models import Student, StudentHistoryGroups, StudentCharity
from subjects.serializers import Subject
from teachers.models import Teacher
from user.models import CustomUser
from branch.models import Branch
from group.models import Group
from rest_framework import serializers
from django.db import transaction


class OldIdRelatedField(serializers.RelatedField):
    def to_internal_value(self, data):
        if isinstance(data, dict):
            old_id = data.get('old_id')
            if old_id is None:
                raise serializers.ValidationError("old_id is required.")
            try:
                return self.get_queryset().get(old_id=old_id)
            except self.get_queryset().model.DoesNotExist:
                raise serializers.ValidationError(f"Object with old_id {old_id} does not exist.")
        raise serializers.ValidationError("Expected a dictionary with an 'old_id'.")

    def to_representation(self, value):
        return {
            'old_id': value.old_id,
            # Add any additional fields you want to include
        }


class StudentSerializerTransfer(serializers.ModelSerializer):
    subject = OldIdRelatedField(queryset=Subject.objects.all(), many=True)
    user = OldIdRelatedField(queryset=CustomUser.objects.all(), many=False)

    class Meta:
        model = Student
        fields = '__all__'
        extra_kwargs = {
            'parents_number': {'required': False, 'allow_blank': True},
            'representative_name': {'required': False, 'allow_blank': True},
            'representative_surname': {'required': False, 'allow_blank': True},
            'total_payment_month': {'required': False},
            'extra_payment': {'required': False, 'allow_blank': True},
            'shift': {'required': False, 'allow_blank': True},
            'debt_status': {'required': False},
            'old_money': {'required': False},
            'group_time_table': {'required': False}
        }

    @transaction.atomic
    def create(self, validated_data):
        user_data = validated_data.pop('user')
        subject_data = validated_data.pop('subject', [])
        user = CustomUser.objects.get(old_id=user_data['old_id']) if isinstance(user_data, dict) else user_data
        student = Student.objects.create(user=user, **validated_data)
        student.subject.clear()
        for subject in subject_data:
            subject_instance = Subject.objects.get(old_id=subject['old_id']) if isinstance(subject, dict) else subject
            student.subject.add(subject_instance)
        return student


class TransferDeletedNewStudentSerializer(serializers.ModelSerializer):
    student = OldIdRelatedField(queryset=Student.objects.all(), many=False)

    class Meta:
        model = DeletedNewStudent
        fields = '__all__'


class StudentHistoryGroupCreateSerializerTransfer(serializers.ModelSerializer):
    student = OldIdRelatedField(queryset=Student.objects.all(), many=False)
    group = OldIdRelatedField(queryset=Group.objects.all(), many=False)
    teacher = OldIdRelatedField(queryset=Teacher.objects.all(), many=False)
    reason = serializers.CharField(required=False, allow_null=True)
    joined_day = serializers.DateField(required=False, allow_null=True)
    left_day = serializers.DateField(required=False, allow_null=True)

    class Meta:
        model = StudentHistoryGroups
        fields = ['id', 'student', 'group', 'teacher', 'reason', 'joined_day', 'left_day', 'old_id']


class StudentCharitySerializerTransfer(serializers.ModelSerializer):
    student = OldIdRelatedField(queryset=Student.objects.all(), many=False)
    group = OldIdRelatedField(queryset=Group.objects.all(), many=False)
    branch = OldIdRelatedField(queryset=Branch.objects.all(), many=False)

    class Meta:
        model = StudentCharity
        fields = ['id', 'charity_sum', 'added_data', 'student', 'old_id', 'branch', 'group']
