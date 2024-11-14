import json
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView

from group.models import Group
from ...models import ClassTimeTable
from ...serializers import ClassTimeTableCreateUpdateSerializers, ClassTimeTableReadSerializers, \
    ClassTimeTableTest2Serializer, ClassTimeTableForClassSerializer2
from ...serializers_list import GroupClassSerializerList, FlowsSerializerList
from teachers.functions.school.CalculateTeacherSalary import teacher_salary_school
from group.serializers import GroupClassSerializer

from time_table.functions.creatWeekDays import creat_week_days
from time_table.models import WeekDays
from flows.models import Flow
from branch.models import Branch
from flows.serializers import FlowsSerializer
from teachers.models import Teacher, TeacherSalary


class CreateClassTimeTable(generics.ListCreateAPIView):
    queryset = ClassTimeTable
    serializer_class = ClassTimeTableCreateUpdateSerializers

    def create(self, request, *args, **kwargs):
        write_serializer = self.get_serializer(data=request.data, partial=True)
        write_serializer.is_valid(raise_exception=True)
        self.perform_create(write_serializer)

        instance = ClassTimeTable.objects.get(pk=write_serializer.data['id'])
        read_serializer = ClassTimeTableReadSerializers(instance)

        teacher_salary_school(request)
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
        # week_id = self.request.query_params.get('week')
        date = self.request.query_params.get('date')
        branch_id = self.request.query_params.get('branch')
        branch = Branch.objects.get(id=branch_id)
        # week = WeekDays.objects.get(id=week_id)
        serializer = ClassTimeTableTest2Serializer(context={'date': date, 'branch': branch})
        data = {
            'time_tables': serializer.get_time_tables(None),
            'hours_list': serializer.get_hours_list(None)
        }
        return Response(data)


class ClassTimeTableForClassView(APIView):
    def get(self, request):
        # week_id = self.request.query_params.get('week')
        date = self.request.query_params.get('date')
        branch_id = self.request.query_params.get('branch')
        branch = Branch.objects.get(id=branch_id)
        # week = WeekDays.objects.get(id=week_id)
        serializer = ClassTimeTableForClassSerializer2(context={'date': date, 'branch': branch})
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
