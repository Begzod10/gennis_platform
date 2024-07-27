from rest_framework import serializers

from group.models import Group
from group.serializers import GroupSerializer
from students.serializers import Student, StudentSerializer
from teachers.models import Teacher
from teachers.serializers import TeacherSerializer
from .models import LessonPlan, LessonPlanStudents


class LessonPlanSerializer(serializers.ModelSerializer):
    teacher = serializers.PrimaryKeyRelatedField(queryset=Teacher.objects.all())
    group = serializers.PrimaryKeyRelatedField(queryset=Group.objects.all())

    class Meta:
        model = LessonPlan
        fields = ['teacher', 'group', 'date']


class LessonPlanGetSerializer(serializers.ModelSerializer):
    teacher = TeacherSerializer(read_only=True)
    group = GroupSerializer(read_only=True)

    class Meta:
        model = LessonPlan
        fields = '__all__'


class LessonPlanStudentSerializer(serializers.ModelSerializer):
    student = serializers.PrimaryKeyRelatedField(queryset=Student.objects.all())
    lesson_plan = serializers.PrimaryKeyRelatedField(queryset=LessonPlan.objects.all())

    class Meta:
        model = LessonPlanStudents
        fields = ['comment', 'comment', 'student']


class LessonPlanStudentGetSerializer(serializers.ModelSerializer):
    student = StudentSerializer(read_only=True)
    lesson_plan = LessonPlanGetSerializer(read_only=True)

    class Meta:
        model = LessonPlanStudents
        fields = ['comment', 'comment', 'student']
