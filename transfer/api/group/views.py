from rest_framework import generics
from rest_framework.response import Response

from group.models import Group, GroupReason, CourseTypes
from group.serializers import GroupSerializer
from .serializers import TransferGroupCreateUpdateSerializer


class TransferCreatGroups(generics.ListCreateAPIView):
    queryset = Group.objects.all()
    serializer_class = TransferGroupCreateUpdateSerializer

    def create(self, request, *args, **kwargs):
        write_serializer = self.get_serializer(data=request.data, partial=True)
        write_serializer.is_valid(raise_exception=True)
        self.perform_create(write_serializer)

        instance = Group.objects.get(pk=write_serializer.data['id'])
        read_serializer = GroupSerializer(instance)
        return Response(read_serializer.data)