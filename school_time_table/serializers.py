from datetime import datetime
from django.db.models import Q
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

from .functions.checkStudentRoomTeacher import check_student_room_teacher


class HoursSerializers(serializers.ModelSerializer):
    class Meta:
        model = Hours
        fields = ['start_time', 'end_time', 'name', 'order']


class ClassTimeTableCreateUpdateSerializers(serializers.ModelSerializer):
    group = serializers.PrimaryKeyRelatedField(queryset=Group.objects.all())
    week = serializers.PrimaryKeyRelatedField(queryset=WeekDays.objects.all())
    room = serializers.PrimaryKeyRelatedField(queryset=Room.objects.all(), allow_null=True, required=False)
    hours = serializers.PrimaryKeyRelatedField(queryset=Hours.objects.all())
    branch = serializers.PrimaryKeyRelatedField(queryset=Branch.objects.all())
    teacher = serializers.PrimaryKeyRelatedField(queryset=Teacher.objects.all())
    subject = serializers.PrimaryKeyRelatedField(queryset=Subject.objects.all())
    flow = serializers.PrimaryKeyRelatedField(queryset=Flow.objects.all())
    name = serializers.CharField()

    class Meta:
        model = ClassTimeTable
        fields = ['id', 'group', 'week', 'room', 'hours', 'branch', 'teacher', 'subject', 'flow', 'name']

    def validate(self, attrs):
        attrs = super().validate(attrs)
        room = attrs.get('room')
        if room == 0:
            attrs['room'] = None
        return attrs

    def create(self, validated_data):
        group = validated_data.get('group')
        flow = validated_data.get('flow')
        students = group.students.all() if group else flow.students.all() if flow else None
        status, errors = check_student_room_teacher(students, validated_data['teacher'], validated_data['room'],
                                                    validated_data['hours'], validated_data['week'])
        if not status:
            raise serializers.ValidationError({"detail": errors})
        class_time_table = ClassTimeTable.objects.create(**validated_data)
        class_time_table.students.add(*students)
        return class_time_table

    def update(self, instance, validated_data):
        group = validated_data.get('group')
        flow = validated_data.get('flow')
        room = validated_data.get('room')
        print(room, 'ascf')
        students = group.students.all() if group else flow.students.all() if flow else None
        status, errors = check_student_room_teacher(students, validated_data['teacher'], validated_data['room'],
                                                    validated_data['hours'], validated_data['week'])
        if not status:
            raise serializers.ValidationError({"detail": errors})
        instance.group = validated_data.get('group', instance.group)
        instance.week = validated_data.get('week', instance.week)
        instance.room = validated_data.get('room', instance.room)
        instance.hours = validated_data.get('hours', instance.hours)
        instance.branch = validated_data.get('branch', instance.branch)
        instance.teacher = validated_data.get('teacher', instance.teacher)
        instance.subject = validated_data.get('subject', instance.subject)
        instance.flow = validated_data.get('flow', instance.flow)
        instance.name = validated_data.get('name', instance.name)
        instance.save()
        return instance


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
