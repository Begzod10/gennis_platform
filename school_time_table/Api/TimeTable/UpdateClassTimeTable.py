import json

from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView

from flows.models import Flow
from ...models import ClassTimeTable
from ...serializers import ClassTimeTableCreateUpdateSerializers, ClassTimeTableReadSerializers
from teachers.functions.school.CalculateTeacherSalary import teacher_salary_school


class UpdateClassTimeTable(generics.RetrieveUpdateDestroyAPIView):
    queryset = ClassTimeTable.objects.all()
    serializer_class = ClassTimeTableCreateUpdateSerializers

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        write_serializer = self.get_serializer(instance, data=request.data, partial=True)
        write_serializer.is_valid(raise_exception=True)
        self.perform_update(write_serializer)

        read_serializer = ClassTimeTableReadSerializers(instance)
        print(request)
        salary_id = request.data.get("salary_id")
        worked_hours = request.data.get("worked_hours", 0)
        class_salary = request.data.get("class_salary")
        type_salary = request.data.get("type_salary", False)

        if salary_id:
            teacher_salary_school(
                salary_id=salary_id,
                worked_hours=worked_hours,
                class_salary=class_salary,
                type_salary=type_salary
            )
        # teacher_salary_school(request)
        return Response({'lesson': read_serializer.data, 'msg': "Dars muvaffaqqiyatli o'zgartirildi"})


class UpdateClassTimeTableHours(APIView):
    def post(self, request):
        branch = self.request.query_params.get('branch')
        status = True
        msg = []
        data = json.loads(request.body)
        lesson_ids = [dt['id'] for dt in data]
        for ls in data:
            if len(data) > 1:
                lesson = ClassTimeTable.objects.get(pk=ls['id'])
                lesson_room = ClassTimeTable.objects.filter(date=ls['date'], room_id=ls['room'],
                                                            hours_id=ls['hour'], branch_id=branch).first()
                if lesson_room:
                    if not lesson_room.id in lesson_ids:
                        status = False
                        msg.append(f"Bu vaqtda '{lesson_room.room.name}' bosh emas")
                lesson_teacher = ClassTimeTable.objects.filter(date=ls['date'], teacher_id=lesson.teacher_id,
                                                               hours_id=ls['hour'], branch_id=branch).first()
                if lesson_teacher:

                    if not lesson_teacher.id in lesson_ids:
                        status = False
                        if lesson_teacher.flow_id == None:
                            msg.append(
                                f"Bu vaqtda '{lesson_teacher.teacher.user.name} {lesson_teacher.teacher.user.surname}' ustozining  '{lesson_teacher.room.name}' xonada  '{lesson_teacher.group.class_number.number}-{lesson_teacher.group.color.name}' sinifiga darsi bor")
                        else:
                            msg.append(
                                f"Bu vaqtda '{lesson_teacher.teacher.user.name} {lesson_teacher.teacher.user.surname}' ustozining  '{lesson_teacher.room.name}' xonada  '{lesson_teacher.flow.name}' patokiga darsi bor")

                students = lesson.group.students.all() if lesson.flow_id == None else lesson.flow.students.all()
                lesson_students = students.filter(class_time_table__hours_id=ls['hour'],
                                                  class_time_table__date=lesson.date,
                                                  class_time_table__branch_id=branch).all()

                if lesson_students:
                    if students:
                        for student in students:
                            tm = student.class_time_table.filter(hours_id=ls['hour'], date=lesson.date,
                                                                 branch_id=branch).first()
                            if not tm.id in lesson_ids:
                                status = False
                                if tm.flow_id == None:
                                    msg.append(
                                        f"Bu vaqtda '{student.user.name} {student.user.surname}' o'quvchisining  '{tm.room.name}' xonasida  '{tm.group.class_number.number}-{tm.group.color.name}' sinifida darsi bor")
                                else:
                                    msg.append(
                                        f"Bu vaqtda '{student.user.name} {student.user.surname}' o'quvchisining  '{tm.room.name}' xonasida  '{tm.flow.name}' patokida darsi bor")
            else:
                lesson = ClassTimeTable.objects.get(pk=ls['id'])
                lesson_room = ClassTimeTable.objects.filter(date=ls['date'], room_id=ls['room'],
                                                            hours_id=ls['hour'], branch_id=branch).first()
                if lesson_room:
                    status = False
                    msg.append(f"Bu vaqtda '{lesson_room.room.name}' bosh emas")
                    lesson_teacher = ClassTimeTable.objects.filter(date=ls['date'], teacher_id=lesson.teacher_id,
                                                                   hours_id=ls['hour'], branch_id=branch).first()
                    if lesson_teacher:
                        status = False
                        if lesson_teacher.flow_id == None:
                            msg.append(
                                f"Bu vaqtda '{lesson_teacher.teacher.user.name} {lesson_teacher.teacher.user.surname}' ustozining  '{lesson_teacher.room.name}' xonada  '{lesson_teacher.group.class_number.number}-{lesson_teacher.group.color.name}' sinifiga darsi bor")
                        else:
                            msg.append(
                                f"Bu vaqtda '{lesson_teacher.teacher.user.name} {lesson_teacher.teacher.user.surname}' ustozining  '{lesson_teacher.room.name}' xonada  '{lesson_teacher.flow.name}' patokiga darsi bor")

                    students = lesson.group.students.all() if lesson.flow_id == None else lesson.flow.students.all()
                    lesson_students = students.filter(class_time_table__hours_id=ls['hour'],
                                                      class_time_table__date=lesson.date,
                                                      class_time_table__branch_id=branch).all()

                    if lesson_students:
                        status = False
                        if students:
                            for student in students:
                                tm = student.class_time_table.filter(hours_id=ls['hour'], date=lesson.date,
                                                                     branch_id=branch).first()
                                if tm.flow_id == None:
                                    msg.append(
                                        f"Bu vaqtda '{student.user.name} {student.user.surname}' o'quvchisining  '{tm.room.name}' xonasida  '{tm.group.class_number.number}-{tm.group.color.name}' sinifida darsi bor")
                                else:
                                    msg.append(
                                        f"Bu vaqtda '{student.user.name} {student.user.surname}' o'quvchisining  '{tm.room.name}' xonasida  '{tm.flow.name}' patokida darsi bor")
                else:
                    if lesson.hours.pk == ls['hour']:

                        lesson_teacher = ClassTimeTable.objects.filter(date=ls['date'], teacher_id=lesson.teacher_id,
                                                                       hours_id=ls['hour'], branch_id=branch,
                                                                       room_id=ls['room']).first()

                        if lesson_teacher:
                            status = False
                            if lesson_teacher.flow_id == None:
                                msg.append(
                                    f"Bu vaqtda '{lesson_teacher.teacher.user.name} {lesson_teacher.teacher.user.surname}' ustozining  '{lesson_teacher.room.name}' xonada  '{lesson_teacher.group.class_number.number}-{lesson_teacher.group.color.name}' sinifiga darsi bor")
                            else:
                                msg.append(
                                    f"Bu vaqtda '{lesson_teacher.teacher.user.name} {lesson_teacher.teacher.user.surname}' ustozining  '{lesson_teacher.room.name}' xonada  '{lesson_teacher.flow.name}' patokiga darsi bor")

                        students = lesson.group.students.all() if lesson.flow_id == None else lesson.flow.students.all()
                        lesson_students = students.filter(class_time_table__hours_id=ls['hour'],
                                                          class_time_table__date=lesson.date,
                                                          class_time_table__branch_id=branch,
                                                          class_time_table__room_id=ls['room']).all()
                        if lesson_students:
                            status = False
                            if students:
                                for student in students:
                                    tm = student.class_time_table.filter(hours_id=ls['hour'], date=lesson.date,
                                                                         branch_id=branch, room_id=ls['room']).first()
                                    if tm.flow_id == None:
                                        msg.append(
                                            f"Bu vaqtda '{student.user.name} {student.user.surname}' o'quvchisining  '{tm.room.name}' xonasida  '{tm.group.class_number.number}-{tm.group.color.name}' sinifida darsi bor")
                                    else:
                                        msg.append(
                                            f"Bu vaqtda '{student.user.name} {student.user.surname}' o'quvchisining  '{tm.room.name}' xonasida  '{tm.flow.name}' patokida darsi bor")
                    else:
                        lesson_teacher = ClassTimeTable.objects.filter(date=ls['date'], teacher_id=lesson.teacher_id,
                                                                       hours_id=ls['hour'], branch_id=branch).first()

                        if lesson_teacher:
                            status = False
                            if lesson_teacher.flow_id == None:
                                msg.append(
                                    f"Bu vaqtda '{lesson_teacher.teacher.user.name} {lesson_teacher.teacher.user.surname}' ustozining  '{lesson_teacher.room.name}' xonada  '{lesson_teacher.group.class_number.number}-{lesson_teacher.group.color.name}' sinifiga darsi bor")
                            else:
                                msg.append(
                                    f"Bu vaqtda '{lesson_teacher.teacher.user.name} {lesson_teacher.teacher.user.surname}' ustozining  '{lesson_teacher.room.name}' xonada  '{lesson_teacher.flow.name}' patokiga darsi bor")

                        students = lesson.group.students.all() if lesson.flow_id == None else lesson.flow.students.all()
                        lesson_students = students.filter(class_time_table__hours_id=ls['hour'],
                                                          class_time_table__date=lesson.date,
                                                          class_time_table__branch_id=branch).all()
                        if lesson_students:
                            status = False
                            if students:
                                for student in students:
                                    tm = student.class_time_table.filter(hours_id=ls['hour'], date=lesson.date,
                                                                         branch_id=branch).first()
                                    if tm.flow_id == None:
                                        msg.append(
                                            f"Bu vaqtda '{student.user.name} {student.user.surname}' o'quvchisining  '{tm.room.name}' xonasida  '{tm.group.class_number.number}-{tm.group.color.name}' sinifida darsi bor")
                                    else:
                                        msg.append(
                                            f"Bu vaqtda '{student.user.name} {student.user.surname}' o'quvchisining  '{tm.room.name}' xonasida  '{tm.flow.name}' patokida darsi bor")

        if status == True:
            for dt in data:
                class_time_table = ClassTimeTable.objects.get(pk=dt['id'])
                class_time_table.room_id = dt['room']
                class_time_table.hours_id = dt['hour']
                class_time_table.save()
        return Response({'status': status, 'msg': msg})


class UpdateFlowTimeTable(APIView):
    def post(self, request):
        status = True
        msg = []
        data = json.loads(request.body)
        room = data.get('room')
        hour = data.get('hour')
        date = data.get('date')
        checked_id = data.get('checked_id')
        flow = Flow.objects.get(pk=checked_id)
        time_table = ClassTimeTable.objects.filter(room_id=room, date=date, hours_id=hour).first()
        if time_table:
            lesson_room = ClassTimeTable.objects.filter(date=date, room_id=room, hours_id=hour).first()

            if lesson_room:
                if not lesson_room.id == time_table.id:
                    status = False
                    msg.append(f'Bu vaqtda {lesson_room.room.name} bosh emas')
            print(room)
            lesson_teacher = ClassTimeTable.objects.filter(date=date,
                                                           room_id=room,
                                                           teacher_id=flow.teacher.pk if flow.teacher else None,
                                                           hours_id=hour).first()
            if lesson_teacher:
                if not lesson_teacher.id == time_table.id:
                    status = False

                    if lesson_teacher.flow_id == None:
                        msg.append(
                            f"Bu vaqtda '{lesson_teacher.teacher.user.name} {lesson_teacher.teacher.user.surname}' ustozining  '{lesson_teacher.room.name}' xonada  '{lesson_teacher.group.class_number.number}-{lesson_teacher.group.color.name}' sinifiga darsi bor")
                    else:
                        msg.append(
                            f"Bu vaqtda '{lesson_teacher.teacher.user.name} {lesson_teacher.teacher.user.surname}' ustozining  '{lesson_teacher.room.name}' xonada  '{lesson_teacher.flow.name}' patokiga darsi bor")

            lesson_students = flow.students.filter(class_time_table__hours_id=hour, class_time_table__date=date).all()

            if lesson_students:
                if flow.students.all():
                    for student in flow.students.all():
                        tm = student.class_time_table.filter(hours_id=hour, date=date).first()
                        if tm:
                            if not tm.id == time_table.id:
                                status = False
                                if tm.flow_id == None:
                                    msg.append(
                                        f'Bu vaqtda {student.user.name} {student.user.surname}ning  "{tm.room.name}" xonasida  "{tm.group.class_number.number}-{tm.group.color.name}" sinifida darsi bor')
                                else:
                                    msg.append(
                                        f'Bu vaqtda {student.user.name} {student.user.surname}ning  "{tm.room.name}" xonasida  "{tm.flow.name}" patokida darsi bor')
            if status == True:
                time_table.delete()
        else:
            lesson_room = ClassTimeTable.objects.filter(date=date, room_id=room, hours_id=hour).first()
            if lesson_room:
                status = False
                msg.append(f'Bu vaqtda {lesson_room.room.name} bosh emas')
            if flow.teacher:
                lesson_teacher = ClassTimeTable.objects.filter(date=date, teacher_id=flow.teacher.pk,
                                                               hours_id=hour).first()
            else:
                lesson_teacher = ClassTimeTable.objects.filter(date=date,
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
                        if tm:

                            if tm.flow_id == None:
                                msg.append(
                                    f'Bu vaqtda {student.user.name} {student.user.surname}ning  "{tm.room.name}" xonasida  "{tm.group.class_number.number}-{tm.group.color.name}" sinifida darsi bor')
                            else:
                                msg.append(
                                    f'Bu vaqtda {student.user.name} {student.user.surname}ning  "{tm.room.name}" xonasida  "{tm.flow.name}" patokida darsi bor')
        return Response({'status': status, 'msg': msg})
