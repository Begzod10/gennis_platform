from django.db.models.query import QuerySet as queryset
from rest_framework import generics
from rest_framework.exceptions import NotFound
from rest_framework.response import Response

from permissions.functions.CheckUserPermissions import check_user_permissions
from teachers.models import TeacherGroupStatistics, Teacher, TeacherSalaryList, TeacherSalary
from teachers.serializers import (
    TeacherSerializerRead, TeacherSalaryListReadSerializers, TeacherGroupStatisticsReadSerializers,
    TeacherSalaryReadSerializers
)
from user.functions.functions import check_auth


class TeacherGroupStatisticsListView(generics.ListAPIView):
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


class TeacherListView(generics.ListAPIView):
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializerRead

    def get_queryset(self):
        branch_id = self.request.query_params.get('branch')
        queryset = Teacher.objects.filter(branches__in=[branch_id]).all()
        return queryset


class TeacherRetrieveView(generics.RetrieveAPIView):
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializerRead

    def get_object(self):
        pk = self.kwargs.get('pk')
        obj = self.get_queryset().filter(pk=pk).first()
        self.check_object_permissions(self.request, obj)

        # calculate_teacher_salary(obj)  # eror bergani uchun yopdim

        return obj


class TeacherSalaryListAPIView(generics.ListAPIView):
    serializer_class = TeacherSalaryListReadSerializers

    def get_queryset(self):
        queryset = TeacherSalaryList.objects.all()
        status = self.request.query_params.get('status', None)
        branch_id = self.request.query_params.get('branch_id', None)
        teacher_salary = self.request.query_params.get('teacher_salary', None)
        if status is not None:
            queryset = queryset.filter(deleted=status)

        if branch_id is not None:
            queryset = queryset.filter(branch_id=branch_id)
        if teacher_salary is not None:
            queryset = queryset.filter(salary_id_id=teacher_salary)

        return queryset


class TeacherSalaryDetailAPIView(generics.RetrieveAPIView):
    queryset = TeacherSalary.objects.all()
    serializer_class = TeacherSalaryReadSerializers

    def retrieve(self, request, *args, **kwargs):
        user, auth_error = check_auth(request)
        if auth_error:
            return Response(auth_error)

        table_names = ['teacher', 'paymenttypes', 'branch', 'customuser']
        permissions = check_user_permissions(user, table_names)
        user_salary_list = self.get_object()

        if isinstance(user_salary_list, queryset):
            user_salary_list_data = self.get_serializer(user_salary_list, many=True).data
        else:
            user_salary_list_data = self.get_serializer(user_salary_list).data

        return Response({'usersalary': user_salary_list_data, 'permissions': permissions})

    def get_object(self):
        user_id = self.kwargs.get('pk')
        try:
            return TeacherSalary.objects.filter(teacher_id=user_id).all()
        except TeacherSalary.DoesNotExist:
            raise NotFound('TeacherSalary not found for the given teacher_id')


class TeacherSalaryListView(generics.ListAPIView):
    serializer_class = TeacherSalaryReadSerializers

    def get_queryset(self):
        queryset = TeacherSalary.objects.all()
        branch_id = self.request.query_params.get('branch_id', None)
        if branch_id is not None:
            queryset = queryset.filter(branch_id=branch_id)
        return queryset


class TeacherSalaryListDetailView(generics.RetrieveAPIView):
    queryset = TeacherSalaryList.objects.all()
    serializer_class = TeacherSalaryListReadSerializers

    def retrieve(self, request, *args, **kwargs):
        user, auth_error = check_auth(request)
        if auth_error:
            return Response(auth_error)

        table_names = ['teachersalarylist', 'teachersalary', 'paymenttypes', 'branch', 'customuser']
        permissions = check_user_permissions(user, table_names)
        user_salary_list = self.get_object()
        user_salary_list_data = self.get_serializer(user_salary_list, many=True).data
        return Response({'teacher_salary': user_salary_list_data, 'permissions': permissions})

    def get_object(self):
        user_id = self.kwargs.get('pk')
        try:
            return TeacherSalaryList.objects.filter(salary_id_id=user_id).all()
        except TeacherSalaryList.DoesNotExist:
            raise NotFound('UserSalary not found for the given user_id')
