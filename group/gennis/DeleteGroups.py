import json
from datetime import datetime

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from gennis_platform.settings import classroom_server
from gennis_platform.uitils import request as send
from group.models import Group
from group.serializers import GroupSerializer
from students.models import StudentHistoryGroups
from teachers.models import TeacherHistoryGroups


class DeleteGroups(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        today = datetime.now()
        group = Group.objects.get(pk=pk)
        # send(url=f"{classroom_server}/delete_group/{group.id}/turon", method='DELETE')
        group.deleted = True
        group.save()
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
            student_history_group = StudentHistoryGroups.objects.filter(group=group, student=student).order_by(
                '-joined_day')
            if student_history_group.exists():
                main_record = student_history_group.first()
                main_record.left_day = today
                main_record.save()

                # Delete all the others
                student_history_group.exclude(id=main_record.id).delete()

            student.save()
        for teacher in group.teacher.all():
            # Get all related history records
            history_qs = TeacherHistoryGroups.objects.filter(group=group, teacher=teacher).order_by(
                '-joined_day')  # or 'created_at'

            if history_qs.exists():
                # Keep the most recent one
                main_record = history_qs.first()
                main_record.left_day = today
                main_record.save()

                # Delete all the others
                history_qs.exclude(id=main_record.id).delete()

            teacher.save()
        for time_table in class_time_tables:
            time_table.delete()
        group.students.clear()
        group.teacher.clear()
        group.save()
        serializer = GroupSerializer(group)
        return Response({'data': serializer.data})

    def get(self, request, pk):
        group = Group.objects.get(pk=pk)
        serializer = GroupSerializer(group)
        return Response({'data': serializer.data})
