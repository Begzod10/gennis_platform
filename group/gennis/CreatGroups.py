from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from group.models import Group, GroupReason, CourseTypes
from group.serializers import GroupSerializer, GroupReasonSerializers, CourseTypesSerializers, \
    GroupCreateUpdateSerializer
from permissions.response import QueryParamFilterMixin


class CreateCourseTypesList(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]

    queryset = CourseTypes.objects.all()
    serializer_class = CourseTypesSerializers


class CourseTypesRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]

    queryset = CourseTypes.objects.all()
    serializer_class = CourseTypesSerializers


class CreateGroupReasonList(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]

    queryset = GroupReason.objects.all()
    serializer_class = GroupReasonSerializers


class GroupReasonRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]

    queryset = GroupReason.objects.all()
    serializer_class = GroupReasonSerializers


class CreatGroups(QueryParamFilterMixin, generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]

    filter_mappings = {
        'teacher': 'teacher__id',
        'subject': 'subject__id',
        'course_types': 'course_types__id',
        'deleted': 'deleted',
        'created_date': 'created_date',
        'branch': 'branch_id'
    }
    serializer_class = GroupCreateUpdateSerializer

    def get_queryset(self):
        queryset = Group.objects.filter(deleted=False).all()
        queryset = self.filter_queryset(queryset)
        return queryset

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
