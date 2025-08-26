from rest_framework import generics,filters
from rest_framework.permissions import IsAuthenticated

from group.models import Group
from group.serializers_list.serializers_self import AddClassesSerializers, TeacherCreateGroupSerializerRead, \
    GroupListSerializer,GroupListSerialize2r
from permissions.response import QueryParamFilterMixin
from teachers.models import Teacher


class ClassesView(QueryParamFilterMixin, generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    filter_mappings = {'branch': 'branch_id', 'teacher': 'teacher__id', 'subject': 'subject_id',
        'course_types': 'course_types_id', 'created_date': 'created_date', 'deleted': 'deleted'}
    queryset = Group.objects.filter(class_number__isnull=False, deleted=False).order_by('class_number__number')
    search_fields = ['name',"class_number__number",'class_number__class_types__name']
    filter_backends = [filters.SearchFilter]
    # queryset = Group.objects.filter(class_number__isnull=False, deleted=False).order_by('class_number__number')
    # groups = Group.objects.filter(class_number__isnull=False, deleted=False).order_by('class_number__number')
    # for gr in groups:
    #     gr.students.clear()
    #     gr.teacher.clear()
    #     gr.deleted = True
    #     gr.save()
    serializer_class = GroupListSerializer


class ClassesView2(QueryParamFilterMixin, generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    filter_mappings = {'branch': 'branch_id', 'teacher': 'teacher__id', 'subject': 'subject_id',
        'course_types': 'course_types_id', 'created_date': 'created_date', 'deleted': 'deleted'}
    queryset = Group.objects.filter(class_number__isnull=False, deleted=False).order_by('class_number__number')
    # queryset = Group.objects.filter(class_number__isnull=False, deleted=False).order_by('class_number__number')
    # groups = Group.objects.filter(class_number__isnull=False, deleted=False).order_by('class_number__number')
    # for gr in groups:
    #     gr.students.clear()
    #     gr.teacher.clear()
    #     gr.deleted = True
    #     gr.save()
    serializer_class = GroupListSerialize2r


class AddClassesList(QueryParamFilterMixin, generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    filter_mappings = {'branch': 'branch_id'}
    queryset = Group.objects.filter(class_number__isnull=False, deleted=False).order_by('class_number__number')
    serializer_class = AddClassesSerializers


class CreateGroupTeacherListView(QueryParamFilterMixin, generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    filter_mappings = {'branch': 'user__branch_id', }
    queryset = Teacher.objects.all()
    serializer_class = TeacherCreateGroupSerializerRead
