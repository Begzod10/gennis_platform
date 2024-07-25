from rest_framework.response import Response
from rest_framework.views import APIView
import json
from group.models import Group
from group.serializers import GroupSerializer
from students.models import Student


class DeleteStudentFromGroup(APIView):
    def post(self, request, pk):
        group = Group.objects.get(pk=pk)
        data = json.loads(request.body)
        for student in data['students']:
            st = Student.objects.get(pk=student)
            class_time_tables = st.class_time_table.filter(group=group).all()
            for class_time_table in class_time_tables:
                class_time_table.students.remove(st)
            group.students.remove(st)
        serializer = GroupSerializer(group)
        return Response({'data': serializer.data})

    def get(self, request, pk):
        group = Group.objects.get(pk=pk)
        serializer = GroupSerializer(group)
        return Response({'data': serializer.data})
