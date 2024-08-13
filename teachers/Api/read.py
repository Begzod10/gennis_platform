from rest_framework import generics

from teachers.functions.school.CalculateTeacherSalary import calculate_teacher_salary
from teachers.models import TeacherGroupStatistics, Teacher, TeacherSalaryList, TeacherSalary
from teachers.serializers import (
    TeacherSerializerRead, TeacherSalaryListReadSerializers, TeacherGroupStatisticsReadSerializers,
    TeacherSalaryReadSerializers
)


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


class TeacherRetrieveView(generics.RetrieveAPIView):
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializerRead

    def get_object(self):
        pk = self.kwargs.get('pk')
        obj = self.get_queryset().filter(pk=pk).first()
        # self.check_object_permissions(self.request, obj)
        # calculate_teacher_salary(obj)
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
    queryset = TeacherSalaryList.objects.all()
    serializer_class = TeacherSalaryListReadSerializers


class TeacherSalaryListView(generics.ListAPIView):
    serializer_class = TeacherSalaryReadSerializers

    def get_queryset(self):
        queryset = TeacherSalary.objects.all()
        branch_id = self.request.query_params.get('branch_id', None)
        if branch_id is not None:
            queryset = queryset.filter(branch_id=branch_id)
        return queryset
