from rest_framework import generics
from rest_framework.response import Response

from group.models import Group, GroupReason, CourseTypes
from group.serializers import GroupSerializer, GroupReasonSerializers, CourseTypesSerializers, \
    GroupCreateUpdateSerializer


class CreateCourseTypesList(generics.ListCreateAPIView):
    queryset = CourseTypes.objects.all()
    serializer_class = CourseTypesSerializers


class CourseTypesRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CourseTypes.objects.all()
    serializer_class = CourseTypesSerializers


class CreateGroupReasonList(generics.ListCreateAPIView):
    queryset = GroupReason.objects.all()
    serializer_class = GroupReasonSerializers


class GroupReasonRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = GroupReason.objects.all()
    serializer_class = GroupReasonSerializers


class CreatGroups(generics.ListCreateAPIView):
    queryset = Group.objects.filter(deleted=False).all()
    serializer_class = GroupCreateUpdateSerializer

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return GroupSerializer
        return GroupCreateUpdateSerializer

    def create(self, request, *args, **kwargs):
        write_serializer = self.get_serializer(data=request.data, partial=True)
        write_serializer.is_valid(raise_exception=True)
        self.perform_create(write_serializer)

        instance = Group.objects.get(pk=write_serializer.data['id'])
        read_serializer = GroupSerializer(instance)
        return Response(read_serializer.data)
