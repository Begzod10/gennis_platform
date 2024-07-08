from rest_framework import serializers

from branch.models import Branch
from language.models import Language
<<<<<<< HEAD
=======
from students.models import Student
from teachers.models import Teacher
>>>>>>> 2398607749231d583f9f93f6743201907f04addb
from teachers.serializers import TeacherSerializer
from teachers.models import Teacher
from .models import Group, StudentHistoryGroups
from subjects.models import Subject, SubjectLevel
from system.models import System

from branch.serializers import BranchSerializer
from language.serializers import LanguageSerializers
from subjects.serializers import SubjectSerializer, SubjectLevelSerializer
from students.serializers import StudentSerializer
from system.serializers import SystemSerializers


class GroupSerializer(serializers.ModelSerializer):
    branch = BranchSerializer()
    language = LanguageSerializers()
    level = SubjectLevelSerializer()
    subject = SubjectSerializer()
    students = StudentSerializer(many=True)
    teacher = TeacherSerializer(many=True)
    system = SystemSerializers()

    class Meta:
        model = Group
        fields = ['id', 'name', 'price', 'status', 'created_date', 'teacher_salary', 'attendance_days',
<<<<<<< HEAD
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
=======
                  'language', 'level', 'subject', 'students', 'teacher', 'system', 'branch']
>>>>>>> 2398607749231d583f9f93f6743201907f04addb

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


