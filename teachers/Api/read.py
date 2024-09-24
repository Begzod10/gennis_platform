from django.db.models.query import QuerySet
from rest_framework import generics
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from permissions.response import QueryParamFilterMixin
from teachers.models import TeacherGroupStatistics, Teacher, TeacherSalaryList, TeacherSalary
from teachers.serializers import (
    TeacherSerializerRead, TeacherSalaryListReadSerializers, TeacherGroupStatisticsReadSerializers,
    TeacherSalaryReadSerializers
)


class TeacherGroupStatisticsListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    # http://ip_adress:8000/Teachers/teacher-statistics-view/?branch_id=3
    queryset = TeacherGroupStatistics.objects.all()
    serializer_class = TeacherGroupStatisticsReadSerializers

    def get_queryset(self):
        branch = self.request.query_params.get('branch_id', None)
        if branch is not None:
            teacher_group_statistics = TeacherGroupStatistics.objects.get(branch=branch)
        else:
            teacher_group_statistics = TeacherGroupStatistics.objects.all()
        return teacher_group_statistics


class TeacherListView(QueryParamFilterMixin, generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    app_name = "O'qtuvchilar"
    filter_mappings = {
        'branch': "user__branch_id",
        'age': 'user__birth_date',
        "subject": 'subject__id',
        'language': 'user__language_id',
        'deleted': 'deleted',

    }
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializerRead

    def get_queryset(self):
        queryset = Teacher.objects.all()
        queryset = self.filter_queryset(queryset)
        return queryset


class TeacherRetrieveView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializerRead

    def get(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        data = serializer.data
        if not instance.teacher_salary_type:
            data['msg'] = "O'qituvchiga toifa tanlanmagan"
        return Response(data)


class TeacherSalaryListAPIView(QueryParamFilterMixin, generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    filter_mappings = {
        'status': 'deleted',
        'branch': 'branch',
        'teacher_salary': 'salary_id',

    }
    queryset = TeacherSalaryList.objects.all()
    serializer_class = TeacherSalaryListReadSerializers

    def get(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.queryset)
        data = self.get_serializer(queryset, many=True).data

        return Response(data)


class TeacherSalaryDetailAPIView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]

    queryset = TeacherSalary.objects.all()
    serializer_class = TeacherSalaryReadSerializers

    def retrieve(self, request, *args, **kwargs):

        user_salary_list = self.get_object()

        if isinstance(user_salary_list, QuerySet):
            user_salary_list_data = self.get_serializer(user_salary_list, many=True).data
        else:
            user_salary_list_data = self.get_serializer(user_salary_list).data

        return Response(user_salary_list_data)

    def get_object(self):
        user_id = self.kwargs.get('pk')
        try:
            return TeacherSalary.objects.filter(teacher_id=user_id).all()
        except TeacherSalary.DoesNotExist:
            raise NotFound('TeacherSalary not found for the given teacher_id')


class TeacherSalaryListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]

    serializer_class = TeacherSalaryReadSerializers

    def get_queryset(self):
        queryset = TeacherSalary.objects.all()
        branch_id = self.request.query_params.get('branch_id', None)
        if branch_id is not None:
            queryset = queryset.filter(branch_id=branch_id)
        return queryset


class TeacherSalaryListDetailView(QueryParamFilterMixin, generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]

    filter_mappings = {
        'status': 'deleted'
    }
    queryset = TeacherSalaryList.objects.all()
    serializer_class = TeacherSalaryListReadSerializers

    def retrieve(self, request, *args, **kwargs):

        user_salary_list = self.get_object()
        user_salary_list = self.filter_queryset(user_salary_list)
        user_salary_list_data = self.get_serializer(user_salary_list, many=True).data
        return Response(user_salary_list_data)

    def get_object(self):
        user_id = self.kwargs.get('pk')
        try:
            return TeacherSalaryList.objects.filter(salary_id_id=user_id).all()
        except TeacherSalaryList.DoesNotExist:
            raise NotFound('UserSalary not found for the given user_id')
