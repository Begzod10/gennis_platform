from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from group.models import Group


from group.serializers import GroupSerializer
from teachers.serializers import Teacher, TeacherSerializer


class TeacherGroupChange(APIView):
    def post(self, request, pk):
        group = get_object_or_404(Group, pk=pk)
        data = request.data
        teacher_id = data.get('teacher')

        if not teacher_id:
            return Response({'error': 'Teacher ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        teacher = get_object_or_404(Teacher, pk=teacher_id)
        statuss = False

        if (group.group_time_table.start_time != teacher.group.group_time_table.start_time and
                group.group_time_table.week != teacher.group.group_time_table.week and
                group.group_time_table.room != teacher.group.group_time_table.room and
                group.group_time_table.end_time != teacher.group.group_time_table.end_time):
            statuss = True

        if statuss:
            teacher.group = None
            teacher.save()
            group.teacher.add(teacher)

        serializer = GroupSerializer(group)
        return Response({'data': serializer.data})

    def get(self, request, pk):
        start_time = request.query_params.get('start_time')
        end_time = request.query_params.get('end_time')
        week = request.query_params.get('week')
        room = request.query_params.get('room')
        teachers = Teacher.objects.all()
        teacher_data = []

        for teacher in teachers:
            status = (start_time != teacher.group.group_time_table.start_time and
                      week != teacher.group.group_time_table.week and
                      room != teacher.group.group_time_table.room and
                      end_time != teacher.group.group_time_table.end_time)
            serializer = TeacherSerializer(teacher)
            data = {
                'teacher': serializer.data,
                'status': status
            }
            teacher_data.append(data)

        return Response(teacher_data)
