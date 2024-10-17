from rest_framework import serializers

from branch.models import Branch
from branch.serializers import BranchSerializer
from students.models import Student
from students.serializers import StudentSerializer
from subjects.models import Subject, SubjectLevel
from subjects.serializers import SubjectSerializer, SubjectLevelSerializer
from teachers.models import Teacher
from teachers.serializers import TeacherSerializer
from .functions.flowClasses import flow_classes
from .models import Flow


class FlowsSerializerTest(serializers.ModelSerializer):
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    teacher_name = serializers.CharField(source='teacher.user.name', read_only=True)
    teacher_surname = serializers.CharField(source='teacher.user.surname', read_only=True)
    student_count = serializers.IntegerField(source='students.count', read_only=True)
    level_name = serializers.CharField(source='level.name', read_only=True)
    branch_name = serializers.CharField(source='branch.name', read_only=True)
    type = serializers.CharField(default='flow', read_only=True)

    class Meta:
        model = Flow
        fields = ['id', 'name', 'level_name', 'activity', 'subject_name', 'teacher_name', 'student_count',
                  'branch_name', 'type', 'classes', 'teacher_surname']
