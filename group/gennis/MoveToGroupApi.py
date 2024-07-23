import json

from rest_framework.response import Response
from rest_framework.views import APIView

from group.models import Group
from students.models import Student

from group.serializers import GroupSerializer


class MoveToGroupApi(APIView):
    def post(self, request, pk):
        group = Group.objects.get(pk=pk)
        data = json.loads(request.body)
        to_group_id = data.get('to_group_id')
        to_group = Group.objects.get(pk=to_group_id)
        students = data.get('students')
        for student in students:
            st = Student.objects.get(pk=student)
            to_group.students.add(st)
        serializer = GroupSerializer(group)
        return Response({'data': serializer.data})

    def get(self, request, pk):
        group = Group.objects.get(pk=pk)
        group_serializer = GroupSerializer(group)
        groups = Group.objects.filter(branch_id=group.branch_id, system_id=group.system_id)
        groups_serializers = GroupSerializer(groups, many=True)
        return Response({'groups': groups_serializers.data, 'group': group_serializer.data})
