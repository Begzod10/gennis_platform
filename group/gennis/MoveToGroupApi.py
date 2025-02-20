import json
from datetime import datetime

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from group.models import Group
from group.serializers import GroupSerializer
from students.models import Student
from students.models import StudentHistoryGroups


class MoveToGroupApi(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        today = datetime.now()
        group = Group.objects.get(pk=pk)
        data = json.loads(request.body)
        to_group_id = data.get('to_group_id')
        to_group = Group.objects.get(pk=to_group_id)
        students = Student.objects.filter(pk__in=data.get('students'))
        reason = data.get('reason')
        errors = []
        for student in students:
            student_status = True
            for st_group in student.groups_student.all():
                for time_table in st_group.group_time_table.all():
                    to_group_time_table = to_group.group_time_table.filter(start_time__gte=time_table.start_time,
                                                                           end_time__lte=time_table.end_time,
                                                                           week=time_table.week,
                                                                           room=time_table.room).first()
                    if to_group_time_table:
                        student_status = False
                        info = f"{student.user.name} {student.user.surname} o'quvchini {st_group.name} guruhida darsi bor"
                        if not info in errors:
                            errors.append(info)
            if student_status:
                student_history_group = StudentHistoryGroups.objects.get(group=group, student=student)
                student_history_group.left_day = today
                student_history_group.reason = reason
                student_history_group.save()
                group.students.remove(student)
                to_group.students.add(student)
                attendances_per_month = student.attendancepermonth_set.filter(group=group,
                                                                              student=student,
                                                                              month_date__gte=today.strftime(
                                                                                  "%Y-%m-%d"),
                                                                              payment=0)
                for attendance in attendances_per_month:
                    attendance.group = to_group
                    if to_group.price:
                        attendance.total_debt = to_group.price
                    attendance.save()
                StudentHistoryGroups.objects.create(group=to_group, student=student,
                                                    teacher=to_group.teacher.all()[0],
                                                    joined_day=today)
        serializer = GroupSerializer(group)
        return Response({'data': serializer.data, 'errors': errors})
