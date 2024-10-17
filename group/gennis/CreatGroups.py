from django.core.exceptions import ObjectDoesNotExist
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from group.models import Group, GroupReason, CourseTypes
from group.serializers import GroupSerializer, GroupReasonSerializers, CourseTypesSerializers, \
    GroupCreateUpdateSerializer
from permissions.response import QueryParamFilterMixin
from time_table.functions.time_table_archive import creat_time_table_archive


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
        branch = self.request.query_params.get('branch')
        queryset = Group.objects.filter(deleted=False).all()
        if branch is not None:
            try:
                from branch.models import Branch
                branch_obj = Branch.objects.get(id=branch)
                if branch_obj.location.system.name == 'school':
                    queryset = queryset.order_by('class_number__number')

            except ObjectDoesNotExist:
                queryset = Group.objects.none()
        queryset = self.filter_queryset(queryset)

        return queryset

    # def get_serializer_class(self):
    #     if self.request.method == 'GET':
    #
    #         return GroupSerializer
    #     return GroupCreateUpdateSerializer

    def get_serializer(self, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        kwargs['context'] = self.get_serializer_context()
        if self.request.method == 'GET':
            kwargs['context']['fields'] = ['id', 'name']
            print(kwargs['context']['fields'])
            return serializer_class(*args, **kwargs)
        return GroupCreateUpdateSerializer

    def create(self, request, *args, **kwargs):

        """
        Create a new Group instance.

        Args:
            request: Request object.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        Returns:
            Response object with the newly created Group instance data.
        """

        write_serializer = self.get_serializer(data=request.data, partial=True)
        write_serializer.is_valid(raise_exception=True)
        self.perform_create(write_serializer)

        instance = Group.objects.get(pk=write_serializer.data['id'])
        read_serializer = GroupSerializer(instance)
        return Response(read_serializer.data)

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        creat_time_table_archive()
        return Response(serializer.data)
