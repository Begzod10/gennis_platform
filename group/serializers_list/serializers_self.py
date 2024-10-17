import pprint
from datetime import datetime

from rest_framework import serializers
from subjects.serializers import SubjectSerializer, SubjectLevelSerializer
from teachers.models import Teacher, TeacherHistoryGroups
from group.models import Group, GroupReason, CourseTypes


class AddClassesSerializers(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['id', 'name', 'branch']


class TeacherCreateGroupSerializerRead(serializers.ModelSerializer):
    class Meta:
        model = Teacher
        fields = ["id", "name", "subject", "color", "total_students"]
