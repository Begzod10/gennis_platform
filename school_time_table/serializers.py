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


class HoursSerializers(serializers.ModelSerializer):
    can_delete = serializers.SerializerMethodField()

    class Meta:
        model = Hours
        fields = ['id', 'start_time', 'end_time', 'name', 'order', 'can_delete', 'types']

    def get_can_delete(self, obj):
        if obj.classtimetable_set.exists():
            return False
        else:
            return True


class ClassTimeTableCreateUpdateSerializers(serializers.ModelSerializer):
    # type = serializers_list.CharField(default=None, allow_blank=True)

    # type = serializer.CharField(default=None, allow_blank=True)

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
        fields = ['id', 'group', 'week', 'room', 'hours', 'branch', 'teacher', 'subject', 'flow', 'name', 'date']

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
        class_time_table = ClassTimeTable.objects.create(**validated_data)
        class_time_table.students.add(*students)
        return class_time_table

    def update(self, instance, validated_data):
        group = validated_data.get('group')
        flow = validated_data.get('flow')
        instance.group = validated_data.get('group', instance.group)
        # instance.week = validated_data.get('week', instance.week)
        instance.week = validated_data.get('date', instance.date)
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
        fields = ['id', 'name', 'start_time', 'end_time', 'types']


class ClassTimeTableSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassTimeTable
        fields = ['id', 'name', 'week', 'hours', 'flow', 'room', 'teacher', 'subject']


from school_time_table.serializers_list import GroupClassSerializerList
from teachers.serializer.lists import ActiveListTeacherSerializerTime


class ClassTimeTableTest2Serializer(serializers.Serializer):
    time_tables = serializers.SerializerMethodField()
    hours_list = serializers.SerializerMethodField()

    def get_time_tables(self, obj):
        date = self.context['date']
        branch = self.context['branch']
        rooms = Room.objects.filter(branch=branch, deleted=False).all()
        hours = Hours.objects.all().order_by('order')
        time_tables = []

        for room in rooms:
            info = {
                'id': room.id,
                'name': room.name,
                'lessons': []
            }
            for hour in hours:
                lesson = room.classtimetable_set.filter(date=date, hours=hour, branch=branch).order_by(
                    'hours__order').first()
                if lesson:
                    group_info = GroupClassSerializerList(lesson.group).data if lesson.group else None
                    flow_info = {'id': lesson.flow.id, 'name': lesson.flow.name,
                                 'classes': lesson.flow.classes} if lesson.flow else None
                    teacher_info = ActiveListTeacherSerializerTime(lesson.teacher).data if lesson.teacher else None
                    subject_info = {'id': lesson.subject.id, 'name': lesson.subject.name} if lesson.subject else None

                    lesson_info = {
                        'id': lesson.id,
                        'status': lesson.hours == hour,
                        'is_flow': True if lesson.flow else False,
                        'group': flow_info if lesson.group == None else group_info,
                        'room': room.id,
                        'teacher': teacher_info,
                        'subject': subject_info,
                        'hours': hour.id
                    }

                    info['lessons'].append(lesson_info)
                else:
                    info['lessons'].append({
                        'group': {},
                        'status': False,
                        'hours': hour.id,
                        'teacher': {},
                        'subject': {},
                        'room': room.id,
                        'is_flow': False,
                    })
            time_tables.append(info)
        return time_tables

    def get_hours_list(self, obj):
        hours = Hours.objects.all().order_by('order')
        return [
            {
                'id': hour.id,
                'name': hour.name,
                'start_time': hour.start_time.strftime('%H:%M'),
                'end_time': hour.end_time.strftime('%H:%M'),
            }
            for hour in hours
        ]


class ClassTimeTableForClassSerializer(serializers.Serializer):
    time_tables = serializers.SerializerMethodField()
    hours_list = serializers.SerializerMethodField()

    def get_time_tables(self, obj):
        week = self.context['week']
        branch = self.context['branch']
        group = self.context['group']
        hours = Hours.objects.all().order_by('order')
        time_tables = []

        info = {
            'id': group.id,
            'name': group.name,
            'lessons': []
        }
        for hour in hours:
            lesson = group.classtimetable_set.filter(week=week, hours=hour, branch=branch).order_by(
                'hours__order').first()
            flow_class_time_table = None
            for student in group.students.all():
                flow_class_time_table = student.class_time_table.filter(week=week, hours=hour, branch=branch,
                                                                        flow__isnull=False).order_by(
                    'hours__order').first()
                if flow_class_time_table:
                    break

            if lesson:
                group_info = GroupClassSerializer(lesson.group).data if lesson.group else None
                flow_info = {'id': lesson.flow.id, 'name': lesson.flow.name,
                             'classes': lesson.flow.classes} if lesson.flow else None
                teacher_info = TeacherSerializer(lesson.teacher).data if lesson.teacher else None
                subject_info = {'id': lesson.subject.id, 'name': lesson.subject.name} if lesson.subject else None
                room_info = {'id': lesson.room.id, 'name': lesson.room.name} if lesson.room else None
                lesson_info = {
                    'id': lesson.id,
                    'status': lesson.hours == hour,
                    'is_flow': True if lesson.flow else False,
                    'group': flow_info if lesson.group == None else group_info,
                    'room': room_info,
                    'teacher': teacher_info,
                    'subject': subject_info,
                    'hours': hour.id
                }

                info['lessons'].append(lesson_info)
            elif flow_class_time_table:
                flow_info = {'id': flow_class_time_table.flow.id, 'name': flow_class_time_table.flow.name,
                             'classes': flow_class_time_table.flow.classes} if flow_class_time_table.flow else None
                teacher_info = TeacherSerializer(
                    flow_class_time_table.teacher).data if flow_class_time_table.teacher else None
                subject_info = {'id': flow_class_time_table.subject.id,
                                'name': flow_class_time_table.subject.name} if flow_class_time_table.subject else None
                room_info = {'id': lesson.room.id, 'name': lesson.room.name} if flow_class_time_table.room else None
                info['lessons'].append({
                    'id': flow_class_time_table.id,
                    'status': flow_class_time_table.hours == hour,
                    'is_flow': True,
                    'group': flow_info,
                    'room': room_info,
                    'teacher': teacher_info,
                    'subject': subject_info,
                    'hours': hour.id
                })
            else:
                info['lessons'].append({
                    'group': {},
                    'status': False,
                    'hours': hour.id,
                    'teacher': {},
                    'subject': {},
                    'room': {},
                    'is_flow': False,
                })
        time_tables.append(info)
        return time_tables

    def get_hours_list(self, obj):
        hours = Hours.objects.all().order_by('order')
        return [
            {
                'id': hour.id,
                'name': hour.name,
                'start_time': hour.start_time.strftime('%H:%M'),
                'end_time': hour.end_time.strftime('%H:%M'),
            }
            for hour in hours
        ]


class ClassTimeTableForClassSerializer2(serializers.Serializer):
    time_tables = serializers.SerializerMethodField()
    hours_list = serializers.SerializerMethodField()

    def get_time_tables(self, obj):
        # week = self.context['week']
        date = self.context['date']
        branch = self.context['branch']
        hours = Hours.objects.all().order_by('order')
        time_tables = {
            'high': [],
            'initial': []
        }
        groups = Group.objects.filter(branch=branch, deleted=False).all().order_by('class_number__number')
        for group in groups:
            info = {
                'id': group.id,
                'name': f'{group.class_number.number}-{group.color.name}',
                'color': group.color.value,
                'lessons': []
            }
            for hour in hours:
                lesson = group.classtimetable_set.filter(date=date, hours=hour, branch=branch).order_by(
                    'hours__order').first()
                flow_class_time_table = None
                for student in group.students.all():
                    flow_class_time_table = student.class_time_table.filter(date=date, hours=hour, branch=branch,
                                                                            flow__isnull=False).order_by(
                        'hours__order').first()
                    if flow_class_time_table:
                        break
                types = [type.name for type in hour.types.all()]
                if lesson:
                    group_info = {'id': group.id,
                                  'name': f'{group.class_number.number}-{group.color.name}'} if lesson.group else None
                    flow_info = {'id': lesson.flow.id, 'name': lesson.flow.name,
                                 'classes': lesson.flow.classes} if lesson.flow else None
                    teacher_info = {'id': lesson.teacher.id, 'name': lesson.teacher.user.name,
                                    'surname': lesson.teacher.user.surname} if lesson.teacher else None
                    subject_info = {'id': lesson.subject.id, 'name': lesson.subject.name} if lesson.subject else None
                    room_info = {'id': lesson.room.id, 'name': lesson.room.name} if lesson.room else None

                    lesson_info = {
                        'id': lesson.id,
                        'status': lesson.hours == hour,
                        'is_flow': True if lesson.flow else False,
                        'group': flow_info if lesson.group == None else group_info,
                        'room': room_info,
                        'teacher': teacher_info,
                        'subject': subject_info,
                        'hours': hour.id
                    }

                    if group.class_number.number in [1, 2, 3, 4, 5, 6] and 'initial' in types:
                        info['lessons'].append(lesson_info)
                    elif group.class_number.number in [7, 8, 9, 10, 11] and 'high' in types:
                        info['lessons'].append(lesson_info)

                elif flow_class_time_table:

                    flow_info = {'id': flow_class_time_table.flow.id, 'name': flow_class_time_table.flow.name,
                                 'classes': flow_class_time_table.flow.classes} if flow_class_time_table.flow else None
                    teacher_info = {'id': flow_class_time_table.teacher.id,
                                    'name': flow_class_time_table.teacher.user.name,
                                    'surname': flow_class_time_table.teacher.user.surname} if flow_class_time_table.teacher else None
                    subject_info = {'id': flow_class_time_table.subject.id,
                                    'name': flow_class_time_table.subject.name} if flow_class_time_table.subject else None
                    room_info = {'id': flow_class_time_table.room.id,
                                 'name': flow_class_time_table.room.name} if flow_class_time_table.room else None
                    if group.class_number.number in [1, 2, 3, 4, 5, 6] and 'initial' in types:
                        info['lessons'].append({
                            'id': flow_class_time_table.id,
                            'status': flow_class_time_table.hours == hour,
                            'is_flow': True,
                            'group': flow_info,
                            'room': room_info,
                            'teacher': teacher_info,
                            'subject': subject_info,
                            'hours': hour.id
                        })
                    elif group.class_number.number in [7, 8, 9, 10, 11] and 'high' in types:
                        info['lessons'].append({
                            'id': flow_class_time_table.id,
                            'status': flow_class_time_table.hours == hour,
                            'is_flow': True,
                            'group': flow_info,
                            'room': room_info,
                            'teacher': teacher_info,
                            'subject': subject_info,
                            'hours': hour.id
                        })
                else:
                    if group.class_number.number in [1, 2, 3, 4, 5, 6] and  'initial' in types:
                        info['lessons'].append({
                            'group': {},
                            'status': False,
                            'hours': hour.id,
                            'teacher': {},
                            'subject': {},
                            'room': {},
                            'is_flow': False,
                        })
                    elif group.class_number.number in [7, 8, 9, 10, 11] and 'high' in types:
                        info['lessons'].append({
                            'group': {},
                            'status': False,
                            'hours': hour.id,
                            'teacher': {},
                            'subject': {},
                            'room': {},
                            'is_flow': False,
                        })

            if group.class_number.number in [1, 2, 3, 4, 5, 6]:
                time_tables['initial'].append(info)
            else:
                time_tables['high'].append(info)
        return time_tables

    def get_hours_list(self, obj):
        hours = Hours.objects.all().order_by('order')
        return [
            {
                'id': hour.id,
                'name': hour.name,
                'start_time': hour.start_time.strftime('%H:%M'),
                'end_time': hour.end_time.strftime('%H:%M'),
            }
            for hour in hours
        ]
