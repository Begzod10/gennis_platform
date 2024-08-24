from rest_framework.response import Response
from rest_framework.views import APIView

from group.models import Group
from group.serializers import GroupSerializer


class DeleteGroups(APIView):
    def post(self, request, pk):
        group = Group.objects.get(pk=pk)
        group.deleted = True
        group.save()
        time_table = group.group_time_table.all()
        for t in time_table:
            for student in group.students.all():
                student.group_time_table.remove(t)
                student.save()
            for teacher in group.teacher.all():
                teacher.group_time_table.remove(t)
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
