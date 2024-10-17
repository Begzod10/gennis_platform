from rest_framework import generics

from group.models import Group
from group.serializers_list.serializers_self import AddClassesSerializers, TeacherCreateGroupSerializerRead, \
    GroupListSerializer

from rest_framework.permissions import IsAuthenticated
from permissions.response import QueryParamFilterMixin
from teachers.models import Teacher


class ClassesView(QueryParamFilterMixin, generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    filter_mappings = {
        'branch': 'branch_id'
    }
    queryset = Group.objects.filter(class_number__isnull=False, deleted=False)
    serializer_class = GroupListSerializer


class AddClassesList(QueryParamFilterMixin, generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    filter_mappings = {
        'branch': 'branch_id'
    }
    queryset = Group.objects.filter(class_number__isnull=True)
    serializer_class = AddClassesSerializers


class CreateGroupTeacherListView(QueryParamFilterMixin, generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    filter_mappings = {
        'branch': 'user__branch_id',
    }
    queryset = Teacher.objects.all()
    serializer_class = TeacherCreateGroupSerializerRead
