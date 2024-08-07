from rest_framework import serializers
from branch.models import Branch
from language.models import Language
from students.models import Student
from subjects.models import Subject, SubjectLevel
from system.models import System
from teachers.models import Teacher
from group.models import Group, CourseTypes
from classes.models import ClassNumber, ClassColors


class TransferGroupCreateUpdateSerializer(serializers.ModelSerializer):
    branch = serializers.SlugRelatedField(queryset=Branch.objects.all(), slug_field='old_id')
    language = serializers.SlugRelatedField(queryset=Language.objects.all(), slug_field='old_id')
    level = serializers.SlugRelatedField(queryset=SubjectLevel.objects.all(), slug_field='old_id')
    subject = serializers.SlugRelatedField(queryset=Subject.objects.all(), slug_field='old_id')
    students = serializers.SlugRelatedField(queryset=Student.objects.all(), slug_field='old_id', many=True)
    teacher = serializers.SlugRelatedField(queryset=Teacher.objects.all(), slug_field='old_id', many=True)
    course_types = serializers.SlugRelatedField(queryset=CourseTypes.objects.all(), slug_field='old_id', required=False)

    class Meta:
        model = Group
        fields = ['id', 'name', 'price', 'status', 'created_date', 'teacher_salary', 'attendance_days',
                  'deleted', 'branch', 'language', 'level', 'subject', 'students', 'teacher', 'system', 'class_number',
                  'color', 'course_types', 'class_number', 'update_method', 'time_table', 'old_id']
