import json
from datetime import datetime

from rest_framework.response import Response
from rest_framework.views import APIView

from group.models import Group
from group.serializers import GroupSerializer
from students.models import StudentHistoryGroups
from teachers.models import TeacherHistoryGroups


class DeleteGroups(APIView):
    def post(self, request, pk):
        data = json.loads(request.body)

        today = datetime.now()
        group = Group.objects.get(pk=pk)
        group.deleted = True
        group.save()
        if data['type'] == "center":
            time_table = group.group_time_table.all()
            for student in group.students.all():
                student_history_group = StudentHistoryGroups.objects.get(group=group, student=student)
                student_history_group.left_day = today
                student_history_group.save()
                for t in time_table:
                    student.group_time_table.remove(t)
                    student.save()

            for teacher in group.teacher.all():
                for t in time_table:
                    teacher.group_time_table.remove(t)
                teacher_history_group = TeacherHistoryGroups.objects.get(group=group, teacher=teacher)
                teacher_history_group.left_day = today
                teacher_history_group.save()
                teacher.save()
            for t in time_table:
                t.delete()
        else:
            class_time_tables = group.classtimetable_set.all()
            for student in group.students.all():
                for time_table in class_time_tables:
                    student.class_time_table.remove(time_table)
                    student.save()
                today = datetime.now()
                date = datetime(today.year, today.month, 1)
                month_date = date.strftime("%Y-%m-%d")
                attendances_per_month = student.attendancepermonth_set.filter(group=group, student=student,
                                                                              month_date__gte=month_date, payment=0)
                for attendance in attendances_per_month:
                    attendance.delete()
                student_history_group = StudentHistoryGroups.objects.get(group=group, student=student)
                student_history_group.left_day = today
                student_history_group.save()
            for teacher in group.teacher.all():
                teacher_history_group = TeacherHistoryGroups.objects.get(group=group, teacher=teacher)
                teacher_history_group.left_day = today
                teacher_history_group.save()
                teacher.save()
            for time_table in class_time_tables:
                time_table.delete()
        group.students.clear()
        group.teacher.clear()
        serializer = GroupSerializer(group)
        return Response({'data': serializer.data})

    def get(self, request, pk):
        group = Group.objects.get(pk=pk)
        serializer = GroupSerializer(group)
        return Response({'data': serializer.data})
