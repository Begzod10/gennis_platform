from rest_framework import serializers

from branch.models import Branch
from language.models import Language
from teachers.serializers import TeacherSerializer
from teachers.models import Teacher
from .models import Group, GroupReason
from students.models import StudentHistoryGroups
from subjects.models import Subject, SubjectLevel
from system.models import System

from branch.serializers import BranchSerializer
from language.serializers import LanguageSerializers
from subjects.serializers import SubjectSerializer, SubjectLevelSerializer
from students.serializers import StudentSerializer
from system.serializers import SystemSerializers


class GroupReasonSerializers(serializers.ModelSerializer):
    class Meta:
        model = GroupReason
        fields = '__all__'


class GroupSerializer(serializers.ModelSerializer):
    id = serializers.CharField(max_length=100, required=True)
    name = serializers.CharField(max_length=100, required=False)
    price = serializers.CharField(max_length=100, required=False)
    status = serializers.CharField(max_length=100, required=False)
    teacher_salary = serializers.CharField(max_length=100, required=False)
    attendance_days = serializers.CharField(max_length=100, required=False)
    branch = BranchSerializer(required=False)
    language = LanguageSerializers(required=False)
    level = SubjectLevelSerializer(required=False)
    subject = SubjectSerializer(required=False)
    students = StudentSerializer(many=True, required=False)
    teacher = TeacherSerializer(many=True, required=False)
    system = SystemSerializers(required=False)

    class Meta:
        model = Group
        fields = ['id', 'name', 'price', 'status', 'created_date', 'teacher_salary', 'attendance_days',
                  'branch', 'language', 'level', 'subject', 'students', 'teacher', 'system']

    def create(self, validated_data):
        students_data = validated_data.pop('students')
        teacher_data = validated_data.pop('teacher')
        subject_data = validated_data.pop('subject')
        level_data = validated_data.pop('level')
        branch_data = validated_data.pop('branch')
        language_data = validated_data.pop('language')
        system_data = validated_data.pop('system')
        subject = Subject.objects.get(name=subject_data['name'])
        level = SubjectLevel.objects.get(name=level_data['name'])
        print(validated_data)
        # print(branch_data['name'])
        # branch = Branch.objects.get(number=branch_data['name'])
        # print(branch)
        system = System.objects.get(name=system_data['name'])
        language = Language.objects.get(name=language_data['name'])
        group = Group.objects.create(name=validated_data['name'], price=validated_data['price'],
                                     language=language,
                                     branch=branch_data,
                                     system=system,
                                     teacher_salary=validated_data['teacher_salary'],
                                     attendance_days=validated_data['attendance_days'], status=False, deleted=False,
                                     level=level, subject=subject)
        for student in students_data:
            teacher = Teacher.objects.get(teacher_data)
            StudentHistoryGroups.objects.create(joined_day=group.created_date, student=student,
                                                group=group, teacher=teacher)
            group.students.add(student)

        group.teacher.add(teacher_data)
        return group

    def update(self, instance, validated_data):
        subject_data = validated_data.pop('subject')
        language_data = validated_data.pop('language')
        level_data = validated_data.pop('level')
        ignore_fields = ['teacher', 'students', 'status', 'deleted']
        for attr, value in validated_data.items():
            if attr not in ignore_fields:
                setattr(instance, attr, value)
                instance.name = validated_data.get("name", instance.name)
                instance.color = validated_data.get("color", instance.color)
                instance.price = validated_data.get("price", instance.price)
                instance.teacher_salary = validated_data.get("teacher_salary", instance.teacher_salary)
                instance.attendance_days = validated_data.get("attendance_days", instance.attendance_days)
                subject = Subject.objects.get(name=subject_data['name'])
                language = Language.objects.get(name=language_data['name'])
                level = SubjectLevel.objects.get(name=level_data['name'])
                instance.subject = subject
                instance.language = language
                instance.level = level
        instance.save()
        return instance
