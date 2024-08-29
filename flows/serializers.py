from rest_framework import serializers

from teachers.models import Teacher
from .models import Flow, FlowTypes
from subjects.models import Subject, SubjectLevel
from students.models import Student

from subjects.serializers import SubjectSerializer, SubjectLevelSerializer
from teachers.serializers import TeacherSerializer
from students.serializers import StudentSerializer
from branch.serializers import BranchSerializer


# class FlowTypesSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = FlowTypes
#         fields = ['id', 'name', 'classes', 'color']
#

class FlowCreateUpdateSerializer(serializers.ModelSerializer):
    subject = serializers.PrimaryKeyRelatedField(queryset=Subject.objects.all())
    teacher = serializers.PrimaryKeyRelatedField(queryset=Teacher.objects.all())
    students = serializers.PrimaryKeyRelatedField(queryset=Student.objects.all(), many=True)
    level = serializers.PrimaryKeyRelatedField(queryset=SubjectLevel.objects.all(), allow_null=True)

    class Meta:
        model = Flow
        fields = ['id', 'name', 'level', 'activity', 'subject', 'teacher', 'students']


class FlowsSerializer(serializers.ModelSerializer):
    subject = SubjectSerializer(read_only=True)
    # flow_type = FlowTypesSerializer(read_only=True)
    teacher = TeacherSerializer(read_only=True)
    students = StudentSerializer(read_only=True, many=True)
    level = SubjectLevelSerializer(read_only=True)
    branch = BranchSerializer(read_only=True)
    type = serializers.CharField(default='flow', read_only=True)

    class Meta:
        model = Flow
        fields = ['id', 'name', 'level', 'activity', 'subject', 'teacher', 'students', 'branch', 'type']
