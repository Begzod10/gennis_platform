from classes.models import ClassNumber, ClassColors
from rest_framework import serializers
from branch.models import Branch
from language.models import Language
from system.models import System
from group.models import Group
from students.models import DeletedNewStudent
from students.models import Student, StudentHistoryGroups, StudentCharity
from subjects.serializers import Subject
from teachers.models import Teacher
from user.models import CustomUser
from branch.models import Branch
from group.models import Group
from rest_framework import serializers
from django.db import transaction
from rooms.models import Room


class OldIdRelatedField(serializers.RelatedField):
    def to_internal_value(self, data):
        if isinstance(data, dict):
            old_id = data.get('turon_old_id')
            if old_id is None:
                raise serializers.ValidationError("turon_old_id is required.")
            try:
                return self.get_queryset().get(turon_old_id=old_id)
            except self.get_queryset().model.DoesNotExist:
                raise serializers.ValidationError(f"Object with turon_old_id {old_id} does not exist.")
        raise serializers.ValidationError("Expected a dictionary with an 'turon_old_id'.")

    def to_representation(self, value):
        return {
            'turon_old_id': value.turon_old_id,
        }


class NameRelatedField(serializers.SlugRelatedField):
    def __init__(self, *args, **kwargs):
        kwargs['slug_field'] = 'name'
        super().__init__(*args, **kwargs)

    def to_internal_value(self, data):
        model = self.queryset.model
        try:
            return model.objects.get(name=data)
        except model.DoesNotExist:
            raise serializers.ValidationError(f"{model.__name__} with name {data} does not exist.")


class NumberRelatedField(serializers.SlugRelatedField):
    def __init__(self, *args, **kwargs):
        kwargs['slug_field'] = 'number'
        super().__init__(*args, **kwargs)

    def to_internal_value(self, data):
        model = self.queryset.model
        try:
            return model.objects.get(number=data)
        except model.DoesNotExist:
            raise serializers.ValidationError(f"{model.__name__} with number {data} does not exist.")


class TransferGroupSerializer(serializers.ModelSerializer):
    branch = serializers.PrimaryKeyRelatedField(queryset=Branch.objects.all())
    language = serializers.PrimaryKeyRelatedField(queryset=Language.objects.all())
    system = serializers.PrimaryKeyRelatedField(queryset=System.objects.all())
    students = OldIdRelatedField(queryset=Student.objects.all(), many=True)
    teacher = OldIdRelatedField(queryset=Teacher.objects.all(), many=True)
    color = NameRelatedField(queryset=ClassColors.objects.all(), required=False, allow_null=True)
    class_number = NumberRelatedField(queryset=ClassNumber.objects.all(), required=False, allow_null=True)

    class Meta:
        model = Group
        fields = ['turon_old_id', 'class_number', 'color', 'name', 'branch', 'language', 'system', 'students',
                  'teacher']

    @transaction.atomic
    def create(self, validated_data):
        students_data = validated_data.pop('students', [])
        teacher_data = validated_data.pop('teacher', [])
        group = Group.objects.create(**validated_data)
        group.students.clear()
        group.teacher.clear()
        for student in students_data:
            subject_instance = Student.objects.get(turon_old_id=student['old_id']) if isinstance(student,
                                                                                                 dict) else student
            group.students.add(subject_instance)
        for teacher in teacher_data:
            subject_instance = Teacher.objects.get(turon_old_id=teacher['old_id']) if isinstance(teacher,
                                                                                                 dict) else teacher
            group.teacher.add(subject_instance)
        return group


class TransferClassNumberSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassNumber
        fields = ['old_id', 'number', 'price']


class TransferRoomSerializer(serializers.ModelSerializer):
    branch = serializers.PrimaryKeyRelatedField(queryset=Branch.objects.all())

    class Meta:
        model = Room
        fields = ['turon_old_id', 'name', 'seats_number', 'electronic_board', 'branch']


class TransferClassColorsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassColors
        fields = ['old_id', 'name']
