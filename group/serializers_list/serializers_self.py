import pprint
from datetime import datetime

from rest_framework import serializers
from subjects.serializers import SubjectSerializer, SubjectLevelSerializer
from teachers.models import Teacher, TeacherHistoryGroups
from group.models import Group, GroupReason, CourseTypes
from students.serializer.lists import UserSerializer


class AddClassesSerializers(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['id', 'name', 'branch']


class TeacherCreateGroupSerializerRead(serializers.ModelSerializer):
    # user = UserSerializer(read_only=True)
    name = serializers.SerializerMethodField(required=False)

    class Meta:
        model = Teacher
        fields = ["id", "name", ]

    def get_name(self, obj):
        return f"{obj.user.name} {obj.user.surname}"
