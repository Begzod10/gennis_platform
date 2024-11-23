from rest_framework import serializers

from branch.models import Branch
from branch.serializers import BranchSerializer
from flows.models import Flow
from flows.serializers import FlowsSerializer
from group.models import Group
from group.serializers import GroupSerializer, GroupClassSerializer
from rooms.models import Room
from rooms.serializers import RoomCreateSerializer
from school_time_table.models import Hours, ClassTimeTable
from subjects.models import Subject
from subjects.serializers import SubjectSerializer
from teachers.models import Teacher
from teachers.serializers import TeacherSerializer
from time_table.models import WeekDays
from time_table.serializers import WeekDaysSerializer


class GroupClassSerializerList(serializers.ModelSerializer):
    class_number = serializers.SerializerMethodField()
    color = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    type = serializers.CharField(default='group', read_only=True)
    class_name = serializers.CharField(source='name')

    class Meta:
        model = Group
        fields = [
            'id', 'name',
            'class_number', 'color', 'type', 'class_name'
        ]

    def get_class_number(self, obj):
        # from classes.serializers import ClassNumberListSerializers
        # return ClassNumberListSerializers(obj.class_number).data
        return obj.class_number.number

    def get_color(self, obj):
        return {
            'id': obj.color.id, 'value': obj.color.value}

    def get_name(self, obj):
        return f"{obj.class_number.number} {obj.color.name}"


class FlowsSerializerList(serializers.ModelSerializer):
    subject_info = serializers.SerializerMethodField()
    teacher_info = serializers.SerializerMethodField()
    type = serializers.CharField(default='flow', read_only=True)

    class Meta:
        model = Flow
        fields = ['id', 'name', 'activity', 'subject_info', 'teacher_info', 'type',
                  'classes']

    def get_teacher_info(self, obj):
        return {
            'id': obj.teacher.id if obj.teacher else None,
            # 'photo': obj.teacher.user.profile_img.url if obj.teacher else None,
            'name': obj.teacher.user.name if obj.teacher else None,
            'surname': obj.teacher.user.surname if obj.teacher else None,
        }

    def get_subject_info(self, obj):
        return {
            'id': obj.subject.id if obj.subject else None,
            'name': obj.subject.name if obj.subject else None
        }
