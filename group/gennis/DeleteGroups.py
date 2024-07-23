from rest_framework.response import Response
from rest_framework.views import APIView

from group.models import Group
from group.serializers import GroupSerializer


class DeleteGroups(APIView):
    def post(self, request, pk):
        group = Group.objects.get(pk=pk)
        group.deleted = True
        serializer = GroupSerializer(group)
        return Response({'data': serializer.data})

    def get(self, request, pk):
        group = Group.objects.get(pk=pk)
        serializer = GroupSerializer(group)
        return Response({'data': serializer.data})
