from datetime import datetime

from rest_framework import serializers

from branch.models import Branch
from group.models import Group
from rooms.models import Room
from school_time_table.models import Hours, ClassTimeTable
from subjects.models import Subject
from teachers.models import Teacher
from time_table.models import WeekDays
from flows.models import Flow

from group.serializers import GroupSerializer
from time_table.serializers import WeekDaysSerializer
from rooms.serializers import RoomSerializer
from branch.serializers import BranchSerializer
from teachers.serializers import TeacherSerializer
from subjects.serializers import SubjectSerializer
from flows.serializers import FlowsSerializer


class HoursSerializers(serializers.ModelSerializer):
    class Meta:
        model = Hours
        fields = ['start_time', 'end_time', 'name', 'order']

    def create(self, validated_data):
        start_time_str = validated_data['start_time']
        start_time = datetime.strptime(start_time_str, "%H:%M").time()
        end_time_str = validated_data['end_time']
        end_time = datetime.strptime(end_time_str, "%H:%M").time()
        return Hours.objects.create(**validated_data, start_time=start_time, end_time=end_time)

    def update(self, instance, validated_data):
        start_time_str = validated_data['start_time']
        start_time = datetime.strptime(start_time_str, "%H:%M").time()
        end_time_str = validated_data['end_time']
        end_time = datetime.strptime(end_time_str, "%H:%M").time()
        instance.start_time = start_time
        instance.end_time = end_time
        instance.name = validated_data.get('name', instance.name)
        instance.order = validated_data.get('order', instance.order)
        instance.save()
        return instance


class ClassTimeTableCreateUpdateSerializers(serializers.ModelSerializer):
    group = serializers.PrimaryKeyRelatedField(queryset=Group.objects.all())
    week = serializers.PrimaryKeyRelatedField(queryset=WeekDays.objects.all())
    room = serializers.PrimaryKeyRelatedField(queryset=Room.objects.all())
    hours = serializers.PrimaryKeyRelatedField(queryset=Hours.objects.all())
    branch = serializers.PrimaryKeyRelatedField(queryset=Branch.objects.all())
    teacher = serializers.PrimaryKeyRelatedField(queryset=Teacher.objects.all())
    subject = serializers.PrimaryKeyRelatedField(queryset=Subject.objects.all())
    flow = serializers.PrimaryKeyRelatedField(queryset=Flow.objects.all())
    name = serializers.CharField()

    class Meta:
        model = ClassTimeTable
        fields = ['id', 'group', 'week', 'room', 'hours', 'branch', 'teacher', 'subject', 'flow', 'name']


class ClassTimeTableReadSerializers(serializers.ModelSerializer):
    group = GroupSerializer()
    week = WeekDaysSerializer()
    room = RoomSerializer()
    hours = HoursSerializers()
    branch = BranchSerializer()
    teacher = TeacherSerializer()
    subject = SubjectSerializer()
    flow = FlowsSerializer()

    class Meta:
        model = ClassTimeTable
        fields = ['id', 'group', 'week', 'room', 'hours', 'branch', 'teacher', 'subject', 'flow', 'name']
