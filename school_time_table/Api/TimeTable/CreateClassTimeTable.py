import json
import requests
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView
from datetime import datetime, timedelta, date

from group.models import Group
from ...models import ClassTimeTable
from ...serializers import ClassTimeTableCreateUpdateSerializers, ClassTimeTableReadSerializers, \
    ClassTimeTableTest2Serializer, ClassTimeTableForClassSerializer2
from ...serializers_list import GroupClassSerializerList, FlowsSerializerList
from group.serializers import GroupClassSerializer

from time_table.functions.creatWeekDays import creat_week_days
from time_table.models import WeekDays
from flows.models import Flow
from branch.models import Branch
from flows.serializers import FlowsSerializer
from teachers.models import Teacher, TeacherSalary
from classes.models import ClassNumberSubjects
from rest_framework import status
from django.db import transaction
from gennis_platform.settings import classroom_server


class CreateClassTimeTable(generics.ListCreateAPIView):
    queryset = ClassTimeTable
    serializer_class = ClassTimeTableCreateUpdateSerializers

    def create(self, request, *args, **kwargs):
        write_serializer = self.get_serializer(data=request.data, partial=True)
        write_serializer.is_valid(raise_exception=True)
        self.perform_create(write_serializer)

        instance = ClassTimeTable.objects.get(pk=write_serializer.data['id'])
        read_serializer = ClassTimeTableReadSerializers(instance)

        payload = {
            "id": instance.id,
            "group": instance.group.id if instance.group else None,
            "week": instance.week.id if instance.week else None,
            "room": instance.room.id if instance.room else None,
            "hours": instance.hours.id if instance.hours else None,
            "branch": instance.branch.id if instance.branch else None,
            "teacher": instance.teacher.id if instance.teacher else None,
            "subject": instance.subject.name if instance.subject else None,
            "flow": instance.flow.id if instance.flow else None,
            "name": instance.name,
            "date": instance.date.isoformat() if instance.date else None,
        }

        requests.post(f"{classroom_server}/api/time_table/timetable-list-create", json=payload)
        # teacher_salary_school(request)

        return Response({'lesson': read_serializer.data, 'msg': 'Dars muvaffaqqiyatli kiritildi'})


class ClassesFlows(generics.ListAPIView):
    def get_queryset(self):
        type = self.request.query_params.get('type')
        branch_id = self.request.query_params.get('branch')
        queryset = None
        if type == 'flow':
            queryset = Flow.objects.filter(branch_id=branch_id)

        if type == 'group':
            queryset = Group.objects.filter(class_number__isnull=False, branch_id=branch_id, deleted=False).order_by(
                'class_number__number')
        return queryset

    def get_serializer_class(self):
        type = self.request.query_params.get('type')
        if type == 'group':
            return GroupClassSerializerList
        else:
            return FlowsSerializerList


# class Classes(generics.ListAPIView):
#     queryset = Group.objects.filter(class_number__isnull=False)
#     serializer_class = GroupSerializer
#     def get_queryset(self):
#         queryset = Group.objects.all()
#         location_id = self.request.query_params.get('location_id', None)
#         branch_id = self.request.query_params.get('branch_id', None)
#
#         if branch_id is not None:
#             queryset = queryset.filter(branch_id=branch_id)
#         if location_id is not None:
#             queryset = queryset.filter(location_id=location_id)
#
#         return queryset


class ClassTimeTableLessonsView(APIView):
    def get(self, request):
        creat_week_days()
        week_id = self.request.query_params.get('week')
        date = self.request.query_params.get('date')
        branch_id = self.request.query_params.get('branch')

        group_id = self.request.query_params.get('group')
        teacher_id = self.request.query_params.get('teacher')
        student_id = self.request.query_params.get('student')

        branch = Branch.objects.get(id=branch_id)
        if week_id:
            week = WeekDays.objects.get(id=week_id)
            date = None
        else:
            week = None

        serializer = ClassTimeTableTest2Serializer(
            context={
                'date': date,
                'branch': branch,
                "week": week,
                "group_id": group_id,
                "teacher_id": teacher_id,
                "student_id": student_id,
            }
        )
        data = {
            'time_tables': serializer.get_time_tables(None),
            'hours_list': serializer.get_hours_list(None)
        }
        return Response(data)


class ClassTimeTableForClassView(APIView):
    def get(self, request):
        week_id = self.request.query_params.get('week')
        date = self.request.query_params.get('date')
        branch_id = self.request.query_params.get('branch')
        branch = Branch.objects.get(id=branch_id)
        if week_id:
            week = WeekDays.objects.get(id=week_id)
            date = None
        else:
            week = None

        serializer = ClassTimeTableForClassSerializer2(context={'date': date, 'branch': branch, "week": week})
        data = {
            'time_tables': serializer.get_time_tables(None),
            'hours_list': serializer.get_hours_list(None)
        }
        return Response(data)


class CheckClassTimeTable(APIView):
    def post(self, request):
        status = True
        msg = []
        data = json.loads(request.body)
        type = data.get('type')
        hour = data.get('hour')
        date = data.get('date')
        checked_id = data.get('checked_id')
        if type == 'group':
            room = data.get('room')
            group = Group.objects.get(pk=checked_id)
            lesson_room = ClassTimeTable.objects.filter(date=date, room_id=room, hours_id=hour).first()
            lesson_students = group.students.filter(class_time_table__hours_id=hour,
                                                    class_time_table__room_id=room,
                                                    class_time_table__date=date).all()
            if lesson_students:
                status = False
                if group.students.all():
                    for student in group.students.all():
                        tm = student.class_time_table.filter(hours_id=hour, date=date).first()
                        if tm.flow_id == None:
                            msg.append(
                                f'Bu vaqtda {student.user.name} {student.user.surname}ning  "{tm.room.name}" xonasida  "{tm.group.class_number.number}-{tm.group.color.name}" sinifida darsi bor')
                        else:
                            msg.append(
                                f'Bu vaqtda {student.user.name} {student.user.surname}ning  "{tm.room.name}" xonasida  "{tm.flow.name}" patokida darsi bor')
            if lesson_room:
                msg.append(f'Bu vaqtda {lesson_room.room.name} bosh emas')
                status = False
        elif type == "subject":
            group_id = data.get('group_id')
            group = Group.objects.get(pk=group_id)
            today = datetime.today()
            start_week = today - timedelta(days=today.weekday())
            week_dates = [(start_week + timedelta(days=i)).date() for i in range(7)]
            class_subject = ClassNumberSubjects.objects.get(subject_id=checked_id, class_number=group.class_number)
            lessons = group.classtimetable_set.filter(date__in=week_dates, subject_id=checked_id).count()
            if int(lessons) >= int(class_subject.hours):
                status = False
                msg.append(
                    f"{group.class_number.number}-{group.color.name} sinifining {class_subject.subject.name} fanining haftalik dars soati to'lgan")
        elif type == 'teacher':
            lesson = ClassTimeTable.objects.filter(date=date, teacher_id=checked_id, hours_id=hour).first()
            if lesson:
                status = False
                if lesson.flow_id == None:
                    msg.append(
                        f"Bu vaqtda '{lesson.teacher.user.name} {lesson.teacher.user.surname}' ustozining  '{lesson.room.name}' xonada  '{lesson.group.class_number.number}-{lesson.group.color.name}' sinifiga darsi bor")
                else:
                    msg.append(
                        f"Bu vaqtda '{lesson.teacher.user.name} {lesson.teacher.user.surname}' ustozining  '{lesson.room.name}' xonada  '{lesson.flow.name}' patokiga darsi bor")

        elif type == 'flow':
            room = data.get('room')
            flow = Flow.objects.get(pk=checked_id)
            lesson_room = ClassTimeTable.objects.filter(date=date, room_id=room, hours_id=hour).first()
            if lesson_room:
                status = False
                msg.append(f'Bu vaqtda {lesson_room.room.name} bosh emas')
            lesson_teacher = ClassTimeTable.objects.filter(date=date, teacher_id=flow.teacher.pk,
                                                           hours_id=hour).first()
            if lesson_teacher:
                status = False
                if lesson_teacher.flow_id == None:
                    msg.append(
                        f"Bu vaqtda '{lesson_teacher.teacher.user.name} {lesson_teacher.teacher.user.surname}' ustozining  '{lesson_teacher.room.name}' xonada  '{lesson_teacher.group.class_number.number}-{lesson_teacher.group.color.name}' sinifiga darsi bor")
                else:
                    msg.append(
                        f"Bu vaqtda '{lesson_teacher.teacher.user.name} {lesson_teacher.teacher.user.surname}' ustozining  '{lesson_teacher.room.name}' xonada  '{lesson_teacher.flow.name}' patokiga darsi bor")

            lesson_students = flow.students.filter(class_time_table__hours_id=hour, class_time_table__date=date).all()

            if lesson_students:
                status = False
                if flow.students.all():
                    for student in flow.students.all():
                        tm = student.class_time_table.filter(hours_id=hour, date=date).first()
                        if tm.flow_id == None:
                            msg.append(
                                f'Bu vaqtda {student.user.name} {student.user.surname}ning  "{tm.room.name}" xonasida  "{tm.group.class_number.number}-{tm.group.color.name}" sinifida darsi bor')
                        else:
                            msg.append(
                                f'Bu vaqtda {student.user.name} {student.user.surname}ning  "{tm.room.name}" xonasida  "{tm.flow.name}" patokida darsi bor')
        return Response({'status': status, 'msg': msg})


class CopyWeekScheduleAPIView(APIView):
    """
    Bir haftalik darslarni boshqa haftaga kochirish API
    """

    def post(self, request):
        source_monday_str = request.data.get("source_monday")
        target_monday_str = request.data.get("target_monday")

        source_monday = date.fromisoformat(source_monday_str)
        target_monday = date.fromisoformat(target_monday_str)

        shift_days = (target_monday - source_monday).days

        source_lessons = ClassTimeTable.objects.filter(
            date__gte=source_monday,
            date__lt=source_monday + timedelta(days=7)
        )

        if not source_lessons.exists():
            return Response({"error": "Manba haftada dars topilmadi"}, status=status.HTTP_404_NOT_FOUND)

        new_lessons = []
        with transaction.atomic():
            for old in source_lessons:
                students = old.students.all()
                old.pk = None
                old.date = old.date + timedelta(days=shift_days)
                old.save()
                old.students.set(students)
                new_lessons.append(old.id)

                try:
                    payload = {
                        "id": old.id,
                        "group": old.group.turon_id if old.group else None,
                        "week": old.week.turon_id if old.week else None,
                        "room": old.room.turon_id if old.room else None,
                        "hours": old.hours.turon_id if old.hours else None,
                        "branch": old.branch.turon_id if old.branch else None,
                        "teacher": old.teacher.turon_id if old.teacher else None,
                        "subject": old.subject.name if old.subject else None,
                        "flow": old.flow.turon_id if old.flow else None,
                        "name": old.name,
                        "date": old.date.isoformat(),
                    }
                    r = requests.post(f"{classroom_server}/api/time_table/timetable-list-create", json=payload)
                    print("Flask response:", r.status_code, r.text)
                except Exception as e:
                    print("Flask create error:", e)

        return Response({
            "message": f"{len(new_lessons)} ta dars nusxalandi",
            "new_ids": new_lessons
        }, status=status.HTTP_201_CREATED)
