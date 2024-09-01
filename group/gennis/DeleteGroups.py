from datetime import datetime

from rest_framework.response import Response
from rest_framework.views import APIView

from group.models import Group
from group.serializers import GroupSerializer
from students.models import StudentHistoryGroups
from time_table.models import TimeTableArchive
from teachers.models import TeacherHistoryGroups
from rest_framework.permissions import IsAuthenticated

class DeleteGroups(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        today = datetime.now()
        group = Group.objects.get(pk=pk)
        group.deleted = True
        group.save()
        time_table = group.group_time_table.all()
        for t in time_table:
            for student in group.students.all():
                student.group_time_table.remove(t)
                student.save()
                student_history_group = StudentHistoryGroups.objects.get(group=group, student=student)
                student_history_group.left_day = today
                student_history_group.save()
            for teacher in group.teacher.all():
                teacher.group_time_table.remove(t)
                teacher_history_group = TeacherHistoryGroups.objects.get(group=group, teacher=teacher)
                teacher_history_group.left_day = today
                teacher.save()
            t.delete()
        group.students.clear()
        group.teacher.clear()
        serializer = GroupSerializer(group)
        return Response({'data': serializer.data})

    def get(self, request, pk):
        group = Group.objects.get(pk=pk)
        serializer = GroupSerializer(group)
        return Response({'data': serializer.data})
