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
from rooms.serializers import RoomCreateSerializer
from branch.serializers import BranchSerializer
from teachers.serializers import TeacherSerializer
from subjects.serializers import SubjectSerializer
from flows.serializers import FlowsSerializer

from .functions.checkStudentRoomTeacher import check_student_room_teacher


class HoursSerializers(serializers.ModelSerializer):
    class Meta:
        model = Hours
        fields = ['id', 'start_time', 'end_time', 'name', 'order']


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
    room = RoomCreateSerializer()
    hours = HoursSerializers()
    branch = BranchSerializer()
    teacher = TeacherSerializer()
    subject = SubjectSerializer()
    flow = FlowsSerializer()

    class Meta:
        model = ClassTimeTable
        fields = ['id', 'group', 'week', 'room', 'hours', 'branch', 'teacher', 'subject', 'flow', 'name']


class DeleteItemTimeTableSerializers(serializers.ModelSerializer):
    item_type = serializers.CharField(default=None, allow_blank=True)

    class Meta:
        model = ClassTimeTable
        fields = ['id', 'group', 'week', 'room', 'hours', 'branch', 'teacher', 'subject', 'flow', 'name', 'item_type']

    def update(self, instance, validated_data):
        item_type = validated_data.get('item_type')
        if item_type:
            setattr(instance, item_type, None)
        instance.save()
        if not any([instance.room, instance.teacher, instance.subject, instance.flow]):
            instance.delete()
            raise serializers.ValidationError({"detail": "dars o'chirildi."})
        return instance


class WeekDaysSerializer(serializers.ModelSerializer):
    class Meta:
        model = WeekDays
        fields = ['id', 'name_en']


class HoursSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hours
        fields = ['id', 'name', 'start_time', 'end_time']


class ClassTimeTableSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassTimeTable
        fields = ['id', 'name', 'week', 'hours', 'flow', 'room', 'teacher', 'subject']


class ClassTimeTableLessonsSerializer(serializers.Serializer):
    time_tables = serializers.SerializerMethodField()
    hours_list = serializers.SerializerMethodField()

    def get_time_tables(self, obj):
        group = self.context['group']
        weekdays = WeekDays.objects.all()
        hours = Hours.objects.all().order_by('order')
        time_tables = []

        for weekday in weekdays:
            info = {
                'weekday': {
                    'id': weekday.id,
                    'name': weekday.name_en,
                    'lessons': []
                },
            }
            for hour in hours:
                lesson = group.classtimetable_set.filter(week=weekday, hours=hour).order_by('hours__order').first()
                if lesson:
                    flow_info = {'id': lesson.flow.id, 'name': lesson.flow.name} if lesson.flow else None
                    room_info = {'id': lesson.room.id, 'name': lesson.room.name} if lesson.room else None
                    teacher_info = {
                        'id': lesson.teacher.id,
                        'name': lesson.teacher.user.name,
                        'surname': lesson.teacher.user.surname
                    } if lesson.teacher else None
                    subject_info = {'id': lesson.subject.id, 'name': lesson.subject.name} if lesson.subject else None

                    lesson_info = {
                        'id': lesson.id,
                        'name': lesson.name,
                        'status': lesson.hours == hour,
                        'flow': flow_info,
                        'room': room_info,
                        'teacher': teacher_info,
                        'subject': subject_info,
                        'hour': {
                            'id': hour.id,
                            'name': hour.name,
                            'start_time': hour.start_time,
                            'end_time': hour.end_time
                        }
                    }

                    info['weekday']['lessons'].append(lesson_info)
                else:
                    info['weekday']['lessons'].append({
                        'status': False,
                        'hour': {
                            'id': hour.id,
                            'name': hour.name,
                            'start_time': hour.start_time,
                            'end_time': hour.end_time
                        }
                    })
            time_tables.append(info)

        return time_tables

    def get_hours_list(self, obj):
        hours = Hours.objects.all().order_by('order')
        return [
            {
                'id': hour.id,
                'name': hour.name,
                'start_time': hour.start_time,
                'end_time': hour.end_time
            }
            for hour in hours
        ]
