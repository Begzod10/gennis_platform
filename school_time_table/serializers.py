from datetime import date, timedelta, datetime
from django.db.models import Q
import requests
from rest_framework import serializers
from django.db.models import F, IntegerField
from branch.models import Branch
from branch.serializers import BranchSerializer
from flows.models import Flow
from flows.serializers import FlowsSerializer
from group.models import Group, GroupSubjects, GroupSubjectsCount
from students.models import Student, StudentSubject, StudentSubjectCount
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
from gennis_platform.settings import classroom_server
from django.db.models import F, Value
from django.db.models.functions import Coalesce
from school_time_table.functions.check_student_subject import all_weekly_counts_equal, weekly_mismatch_details
from school_time_table.serializers_list import GroupClassSerializerList
from teachers.serializer.lists import ActiveListTeacherSerializerTime
from django.db.models.functions import Coalesce, Cast
from django.db.models import F, BigIntegerField, IntegerField
import requests


class HoursSerializers(serializers.ModelSerializer):
    can_delete = serializers.SerializerMethodField()

    class Meta:
        model = Hours
        fields = ['id', 'start_time', 'end_time', 'name', 'order', 'can_delete']

    def get_can_delete(self, obj):
        if obj.classtimetable_set.exists():
            return False
        else:
            return True


class ClassTimeTableCreateUpdateSerializers(serializers.ModelSerializer):
    group = serializers.PrimaryKeyRelatedField(queryset=Group.objects.all())
    week = serializers.PrimaryKeyRelatedField(queryset=WeekDays.objects.all())
    room = serializers.PrimaryKeyRelatedField(queryset=Room.objects.all(), allow_null=True, required=False)
    hours = serializers.PrimaryKeyRelatedField(queryset=Hours.objects.all())
    branch = serializers.PrimaryKeyRelatedField(queryset=Branch.objects.all())
    teacher = serializers.PrimaryKeyRelatedField(queryset=Teacher.objects.all(), required=False, allow_null=True)
    subject = serializers.PrimaryKeyRelatedField(queryset=Subject.objects.all(), required=False, allow_null=True)
    flow = serializers.PrimaryKeyRelatedField(queryset=Flow.objects.all())
    name = serializers.CharField()

    class Meta:
        model = ClassTimeTable
        fields = ['id', 'group', 'week', 'room', 'hours', 'branch', 'teacher', 'subject', 'flow', 'name', 'date']

    def validate(self, attrs):
        attrs = super().validate(attrs)
        room = attrs.get('room')
        # If your client sometimes posts 0 instead of null for room:
        if room == 0:
            attrs['room'] = None
        return attrs

    def create(self, validated_data):
        group = validated_data.get('group')
        flow = validated_data.get('flow')
        lesson_date = validated_data.get('date')  # expected to be a date/datetime
        subject = validated_data.get('subject')

        students = group.students.all() if group else (flow.students.all() if flow else [])
        subject = subject or (flow.subject if flow else None)

        print(flow)
        if flow:
            class_time_table = ClassTimeTable.objects.create(**validated_data, classes=flow.classes)
        else:
            class_time_table = ClassTimeTable.objects.create(**validated_data)
        if students:
            class_time_table.students.add(*students)

        ref_date = lesson_date.date() if hasattr(lesson_date, "date") else lesson_date
        monday = ref_date - timedelta(days=ref_date.weekday())
        friday = monday + timedelta(days=4)
        group_subjects_set = set()

        if group and subject:
            group_subjects = GroupSubjects.objects.filter(group=group, subject=subject).first()
            if group_subjects:
                # Ensure a per-lesson GroupSubjectsCount row exists
                gsc = GroupSubjectsCount.objects.filter(
                    class_time_table=class_time_table,
                    group_subjects=group_subjects
                ).first()
                if not gsc:
                    GroupSubjectsCount.objects.create(
                        class_time_table=class_time_table,
                        group_subjects=group_subjects,
                        date=ref_date,  # store actual lesson date
                    )
                # Recalculate the weekly total (Mon→Fri) and store it on GroupSubjects.count
                weekly_group_total = GroupSubjectsCount.objects.filter(
                    group_subjects=group_subjects,
                    date__gte=monday,
                    date__lte=friday,
                ).count()
                print(weekly_group_total)
                if getattr(group_subjects, "count", None) != weekly_group_total:
                    group_subjects.count = weekly_group_total
                    group_subjects.save(update_fields=["count"])
        if subject:
            for student in students:
                student_subject = StudentSubject.objects.filter(
                    student=student,
                    subject=subject
                ).first()
                if student_subject:
                    if student_subject.group_subjects:
                        group_subjects_set.add(student_subject.group_subjects)
                if not student_subject:
                    continue
                ssc = StudentSubjectCount.objects.filter(
                    class_time_table=class_time_table,
                    student_subjects=student_subject
                ).first()
                if not ssc:
                    StudentSubjectCount.objects.create(
                        class_time_table=class_time_table,
                        student_subjects=student_subject,
                        date=ref_date,  # store actual lesson date
                    )
                weekly_student_total = StudentSubjectCount.objects.filter(
                    student_subjects=student_subject,
                    date__gte=monday,
                    date__lte=friday,
                ).count()

                if getattr(student_subject, "count", None) != weekly_student_total:
                    student_subject.count = weekly_student_total
                    student_subject.save(update_fields=["count"])
        for gs in group_subjects_set:
            status, agg = all_weekly_counts_equal(gs, monday, friday)  # or the Min/Max on `count`
            if not status:
                details = weekly_mismatch_details(gs, monday, friday)
            else:
                gs = GroupSubjects.objects.get(id=gs.id)
                gs.count = agg['min_w']
                gs.save(update_fields=["count"])
        return class_time_table

    def update(self, instance, validated_data):
        group = validated_data.get('group')
        flow = validated_data.get('flow')
        instance.group = validated_data.get('group', instance.group)
        instance.week = validated_data.get('week', instance.week)
        instance.date = validated_data.get('date', instance.date)
        instance.room = validated_data.get('room', instance.room)
        instance.hours = validated_data.get('hours', instance.hours)
        instance.branch = validated_data.get('branch', instance.branch)
        instance.teacher = validated_data.get('teacher', instance.teacher)
        instance.subject = validated_data.get('subject', instance.subject)
        instance.flow = validated_data.get('flow', instance.flow)
        instance.name = validated_data.get('name', instance.name)
        instance.save()

        # flask_url = f"{classroom_server}/api/time_table/timetable-list-update/{instance.id}"
        payload = {}

        if instance.group:
            payload["group"] = instance.group.id
        if instance.week:
            payload["week"] = instance.week.id
        if instance.room:
            payload["room"] = instance.room.id
        if instance.hours:
            payload["hours"] = instance.hours.id
        if instance.branch:
            payload["branch"] = instance.branch.id
        if instance.teacher:
            payload["teacher"] = instance.teacher.id
        if instance.subject:
            payload["subject"] = instance.subject.name
        if instance.flow:
            payload["flow"] = instance.flow.id
        if instance.name:
            payload["name"] = instance.name
        if instance.date:
            payload["date"] = instance.date.isoformat()

        # try:
        #     response = requests.patch(
        #         flask_url,
        #         json=payload,
        #         headers={"Content-Type": "application/json"}
        #     )
        #     response.raise_for_status()
        # except Exception as e:
        #     print("Flask update error:", e)
        return instance

    def delete_from_flask(self, instance):

        flask_url = f"{classroom_server}/api/time_table/timetable-list-delete/{instance.id}"
        print(flask_url, "delete_from_flask")
        if flask_url:
            response = requests.delete(flask_url)
            try:
                data = response.json()
            except ValueError:
                data = {"message": "No JSON response"}
            return data, response.status_code


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


from school_time_table.serializers_list import GroupClassSerializerList
from teachers.serializer.lists import ActiveListTeacherSerializerTime


class ClassTimeTableTest2Serializer(serializers.Serializer):
    time_tables = serializers.SerializerMethodField()
    hours_list = serializers.SerializerMethodField()

    def get_time_tables(self, obj):
        date_ls = self.context.get('date')
        branch = self.context['branch']
        week = self.context.get('week')
        group_id = self.context.get('group_id')
        teacher_id = self.context.get('teacher_id')
        student_id = self.context.get('student_id')

        # Convert date string → date
        if date_ls and isinstance(date_ls, str):
            date_ls = datetime.strptime(date_ls, "%Y-%m-%d").date()

        # Treat week as integer 1..7 (Mon..Sun). If invalid, set to None.
        if isinstance(week, str):
            try:
                week = int(week)
            except ValueError:
                week = None
        if isinstance(week, int):
            if not (1 <= week <= 7):
                week = None

        # Rooms ordered by 'order' (if present) else by id, with consistent output_field
        rooms = (
            Room.objects
            .filter(branch=branch, deleted=False)
            .annotate(
                sort_order=Coalesce(
                    Cast('order', BigIntegerField()),
                    F('id'),
                    output_field=BigIntegerField()
                )
            )
            .order_by('sort_order')
        )

        hours = Hours.objects.all().order_by('order')

        time_tables = []
        week_days = ['Dushanba', 'Seshanba', 'Chorshanba',
                     'Payshanba', 'Juma', 'Shanba', 'Yakshanba']

        # If week (1..7) provided without specific date: compute that weekday in current week
        if week and date_ls is None:
            today = date.today()
            today_weekday = today.isoweekday()  # 1..7
            shift_days = week.order - today_weekday
            week_day_date = today + timedelta(days=shift_days)

            weekday_name = week_days[week_day_date.weekday()]
            rooms_info = self._build_rooms_info(
                rooms, hours, week_day_date,
                branch, week, group_id, teacher_id, student_id
            )
            time_tables.append({
                "date": week_day_date.strftime("%Y-%m-%d"),
                "weekday": weekday_name,
                "rooms": rooms_info
            })


        elif date_ls is None and week is None:
            today = date.today()
            start_week = today - timedelta(days=today.weekday())
            for i in range(7):
                day_date = start_week + timedelta(days=i)
                weekday_name = week_days[day_date.weekday()]
                rooms_info = self._build_rooms_info(
                    rooms, hours, day_date,
                    branch, None, group_id, teacher_id, student_id
                )
                time_tables.append({
                    "date": day_date.strftime("%Y-%m-%d"),
                    "weekday": weekday_name,
                    "rooms": rooms_info
                })


        elif date_ls:
            weekday_name = week_days[date_ls.weekday()]
            rooms_info = self._build_rooms_info(
                rooms, hours, date_ls,
                branch, None, group_id, teacher_id, student_id
            )
            time_tables.append({
                "date": date_ls.strftime("%Y-%m-%d"),
                "weekday": weekday_name,
                "rooms": rooms_info
            })

        return time_tables

    def _build_rooms_info(self, rooms, hours, current_date,
                          branch, week, group_id, teacher_id, student_id):
        """
        week is expected to be int (1..7) or None.
        """
        rooms_info = []
        for room in rooms:
            info = {
                'id': room.id,
                'name': room.name,
                'order': room.order,
                'lessons': []
            }
            for hour in hours:
                qs = room.classtimetable_set.filter(
                    date=current_date,
                    hours=hour,
                    branch=branch
                )
                if week:
                    qs = qs.filter(week=week)  # int-based week
                if group_id:
                    group_id = int(group_id)
                    qs = qs.filter(
                        Q(group_id=group_id) |
                        Q(classes__contains=[group_id])
                    )

                if teacher_id:
                    qs = qs.filter(teacher_id=teacher_id)
                if student_id:
                    qs = qs.filter(group__students__id=student_id)

                lesson = qs.order_by('hours__order').first()

                if lesson:
                    group_info = GroupClassSerializerList(lesson.group).data if lesson.group else None
                    flow_info = {
                        'id': lesson.flow.id,
                        'name': lesson.flow.name,
                        'classes': lesson.flow.classes
                    } if getattr(lesson, 'flow', None) else None
                    teacher_info = ActiveListTeacherSerializerTime(lesson.teacher).data if lesson.teacher else None
                    subject_info = {
                        'id': lesson.subject.id,
                        'name': lesson.subject.name
                    } if lesson.subject else None
                    print(lesson.id)

                    lesson_info = {
                        'id': lesson.id,
                        'status': lesson.hours == hour,
                        'is_flow': True if flow_info else False,
                        'group': flow_info if lesson.group is None else group_info,
                        'room': room.id,
                        'teacher': teacher_info,
                        'subject': subject_info,
                        'hours': hour.id,
                        'students': list(lesson.students.values_list('id', flat=True))
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
                        'students': []
                    })
            rooms_info.append(info)
        return rooms_info

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
                    'hours': hour.id,
                    'date': lesson.date.isoformat() if lesson.date else None,
                    'students': list(lesson.students.values_list('id', flat=True))
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
                    'hours': hour.id,
                    'date': lesson.date.isoformat() if lesson.date else None,
                    'students': list(flow_class_time_table.students.values_list('id', flat=True))
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
                    'date': '',
                    'students': []
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


# class ClassTimeTableForClassSerializer2(serializers.Serializer):
#     time_tables = serializers.SerializerMethodField()
#     hours_list = serializers.SerializerMethodField()
#
#     def get_time_tables(self, obj):
#         date_ls = self.context['date']
#         branch = self.context['branch']
#         week = self.context['week']
#         hours = Hours.objects.all().order_by('order')
#         time_tables = []
#         groups = Group.objects.filter(branch=branch, deleted=False).all().order_by('class_number__number')
#         for group in groups:
#             info = {
#                 'id': group.id,
#                 'name': f'{group.class_number.number}-{group.color.name}',
#                 'color': group.color.value,
#                 'lessons': []
#             }
#
#             for hour in hours:
#                 if week and date_ls == None:
#                     today = date.today()
#                     today_weekday = today.isoweekday()
#                     shift_days = week.order - today_weekday
#                     week_day_date = today + timedelta(days=shift_days)
#                     lesson = group.classtimetable_set.filter(date=week_day_date, hours=hour, branch=branch,
#                                                              week=week).order_by(
#                         'hours__order').first()
#                 else:
#                     lesson = group.classtimetable_set.filter(date=date_ls, hours=hour, branch=branch).order_by(
#                         'hours__order').first()
#                 flow_class_time_table = None
#                 for student in group.students.all():
#                     flow_class_time_table = student.class_time_table.filter(date=date_ls, hours=hour, branch=branch,
#                                                                             flow__isnull=False).order_by(
#                         'hours__order').first()
#                     if flow_class_time_table:
#                         break
#
#                 if lesson:
#                     group_info = {'id': group.id,
#                                   'name': f'{group.class_number.number}-{group.color.name}'} if lesson.group else None
#                     flow_info = {'id': lesson.flow.id, 'name': lesson.flow.name,
#                                  'classes': lesson.flow.classes} if lesson.flow else None
#                     teacher_info = {'id': lesson.teacher.id, 'name': lesson.teacher.user.name,
#                                     'surname': lesson.teacher.user.surname} if lesson.teacher else None
#                     subject_info = {'id': lesson.subject.id, 'name': lesson.subject.name} if lesson.subject else None
#                     room_info = {'id': lesson.room.id, 'name': lesson.room.name} if lesson.room else None
#                     lesson_info = {
#                         'id': lesson.id,
#                         'status': lesson.hours == hour,
#                         'is_flow': True if lesson.flow else False,
#                         'group': flow_info if lesson.group == None else group_info,
#                         'room': room_info,
#                         'teacher': teacher_info,
#                         'subject': subject_info,
#                         'hours': hour.id,
#                         'date': lesson.date.isoformat() if lesson.date else None
#                     }
#
#                     info['lessons'].append(lesson_info)
#                 elif flow_class_time_table:
#                     flow_info = {'id': flow_class_time_table.flow.id, 'name': flow_class_time_table.flow.name,
#                                  'classes': flow_class_time_table.flow.classes} if flow_class_time_table.flow else None
#                     teacher_info = {'id': flow_class_time_table.teacher.id,
#                                     'name': flow_class_time_table.teacher.user.name,
#                                     'surname': flow_class_time_table.teacher.user.surname} if flow_class_time_table.teacher else None
#                     subject_info = {'id': flow_class_time_table.subject.id,
#                                     'name': flow_class_time_table.subject.name} if flow_class_time_table.subject else None
#                     room_info = {'id': flow_class_time_table.room.id,
#                                  'name': flow_class_time_table.room.name} if flow_class_time_table.room else None
#                     info['lessons'].append({
#                         'id': flow_class_time_table.id,
#                         'status': flow_class_time_table.hours == hour,
#                         'is_flow': True,
#                         'group': flow_info,
#                         'room': room_info,
#                         'teacher': teacher_info,
#                         'subject': subject_info,
#                         'hours': hour.id,
#                         'date': flow_class_time_table.date.isoformat() if flow_class_time_table.date else None
#                     })
#                 else:
#                     info['lessons'].append({
#                         'group': {},
#                         'status': False,
#                         'hours': hour.id,
#                         'teacher': {},
#                         'subject': {},
#                         'room': {},
#                         'is_flow': False,
#                         'date': ''
#                     })
#
#             time_tables.append(info)
#         return time_tables
#
#     def get_hours_list(self, obj):
#         hours = Hours.objects.all().order_by('order')
#         return [
#             {
#                 'id': hour.id,
#                 'name': hour.name,
#                 'start_time': hour.start_time.strftime('%H:%M'),
#                 'end_time': hour.end_time.strftime('%H:%M'),
#             }
#             for hour in hours
#         ]


from collections import defaultdict
from datetime import date, timedelta
from rest_framework import serializers

class ClassTimeTableForClassSerializer2(serializers.Serializer):
    time_tables = serializers.SerializerMethodField()
    hours_list = serializers.SerializerMethodField()

    def get_time_tables(self, obj):
        branch = self.context['branch']
        date_ls = self.context.get('date')
        week = self.context.get('week')

        hours = Hours.objects.all().order_by('order')
        groups = Group.objects.filter(
            branch=branch,
            deleted=False
        ).select_related('class_number', 'color').order_by('class_number__number')

        hours_list = [
            f"{h.start_time.strftime('%H:%M')}-{h.end_time.strftime('%H:%M')}"
            for h in hours
        ]

        classes = []
        group_index_map = {}

        for idx, g in enumerate(groups):
            classes.append({
                "name": f"{g.class_number.number}-{g.color.name}",
                "index": idx
            })
            group_index_map[g.id] = idx

        subjects = []

        for hour_index, hour in enumerate(hours):

            if week and date_ls is None:
                today = date.today()
                shift = week.order - today.isoweekday()
                lesson_date = today + timedelta(days=shift)
            else:
                lesson_date = date_ls

            hour_lessons = defaultdict(list)

            for group in groups:

                lessons = list(
                    group.classtimetable_set.filter(
                        date=lesson_date,
                        hours=hour,
                        branch=branch
                    ).select_related(
                        'subject', 'teacher__user', 'room', 'flow'
                    )
                )

                for student in group.students.all():
                    lessons += list(
                        student.class_time_table.filter(
                            date=lesson_date,
                            hours=hour,
                            branch=branch,
                            flow__isnull=False
                        ).select_related(
                            'subject', 'teacher__user', 'room', 'flow'
                        )
                    )

                for lesson in lessons:
                    if not lesson.subject and not lesson.flow:
                        continue

                    # 🔥 TO‘G‘RI KEY
                    if lesson.flow:
                        key = ("flow", lesson.flow.id)
                    else:
                        key = (
                            "lesson",
                            lesson.subject.id if lesson.subject else None,
                            lesson.teacher.id if lesson.teacher else None,
                            lesson.room.id if lesson.room else None,
                        )

                    hour_lessons[key].append((lesson, group))

            for _, lesson_group_list in hour_lessons.items():
                lesson_obj = lesson_group_list[0][0]
                is_flow = bool(lesson_obj.flow)

                involved_group_ids = list({
                    g.id for _, g in lesson_group_list
                })

                class_indexes = [
                    group_index_map[g_id]
                    for g_id in involved_group_ids
                ]

                groups_data = None
                if is_flow or len(class_indexes) > 1:
                    flow_groups = Group.objects.filter(
                        id__in=involved_group_ids
                    ).select_related('class_number', 'color')

                    groups_data = [
                        {"name": f"{g.class_number.number}-{g.color.name}"}
                        for g in flow_groups
                    ]

                subjects.append({
                    "hourIndex": hour_index,
                    "classes": class_indexes,
                    "groups": None,

                    "name": lesson_obj.subject.name if lesson_obj.subject else lesson_obj.flow.name,
                    "is_flow": is_flow,

                    "subject": {
                        "name": lesson_obj.subject.name
                    } if lesson_obj.subject else None,

                    "teacher": {
                        "name": lesson_obj.teacher.user.name
                        if lesson_obj.teacher else None
                    },

                    "room": {
                        "name": lesson_obj.room.name
                        if lesson_obj.room else None
                    }
                })

        return {
            "hours": hours_list,
            "classes": classes,
            "subjects": subjects
        }

    def get_hours_list(self, obj):
        hours = Hours.objects.all().order_by('order')
        return [
            {
                'id': h.id,
                'name': h.name,
                'start_time': h.start_time.strftime('%H:%M'),
                'end_time': h.end_time.strftime('%H:%M'),
            }
            for h in hours
        ]