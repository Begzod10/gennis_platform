from rest_framework import serializers

from branch.models import Branch
from language.models import Language
from students.models import Student
from teachers.models import Teacher
from teachers.serializers import TeacherSerializer
from .models import Group
from subjects.models import Subject, SubjectLevel
from system.models import System

from branch.serializers import BranchSerializer
from language.serializers import LanguageSerializers
from subjects.serializers import SubjectSerializer, SubjectLevelSerializer
from students.serializers import StudentSerializer
from system.serializers import SystemSerializers
from group.serializers import GroupSerializer


class AttendancePerMonthSerializer(serializers.ModelSerializer):
    student = StudentSerializer()
    teacher = TeacherSerializer()
    group = GroupSerializer()

    class Meta:
        model = Group
        fields = ['id', 'date', 'status', 'total_debt', 'total_salary', 'ball_percentage', 'month_date',
                  'total_charity', 'remaining_debt', 'payment', 'remaining_salary', 'teacher', 'student',
                  'taken_salary', 'group']
    # def create(self, validated_data):
    #     user_data = validated_data.pop('user')
    #     user = CustomUser.objects.create(**user_data)
    #     student = Student.objects.create(user=user, **validated_data)
    #     return student
