from rest_framework import generics, status
from rest_framework.response import Response
from .models import TeacherGroupStatistics, Teacher, TeacherSalaryList, TeacherSalary
from .functions.school.CalculateTeacherSalary import calculate_teacher_salary

from .serializers import (
    TeacherSerializer, TeacherSalaryListSerializers, TeacherGroupStatisticsSerializers, TeacherSalarySerializers
)


class TeacherGroupStatisticsListView(generics.ListAPIView):
    # http://ip_adress:8000/Teachers/teacher-statistics-view/?branch_id=3
    queryset = TeacherGroupStatistics.objects.all()
    serializer_class = TeacherGroupStatisticsSerializers

    def get_queryset(self):
        branch = self.request.query_params.get('branch_id', None)
        if branch is not None:
            teacher_group_statistics = TeacherGroupStatistics.objects.get(branch=branch)
        else:
            teacher_group_statistics = TeacherGroupStatistics.objects.all()
        return teacher_group_statistics


class TeacherListCreateView(generics.ListCreateAPIView):
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer


class TeacherRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer

    def get_object(self):
        pk = self.kwargs.get('pk')
        obj = self.get_queryset().filter(pk=pk).first()
        # self.check_object_permissions(self.request, obj)
        calculate_teacher_salary(obj)
        return super().get_object()


class TeacherSalaryListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = TeacherSalaryListSerializers

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

    def perform_create(self, serializer):
        serializer.save()


class TeacherSalaryListDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = TeacherSalaryList.objects.all()
    serializer_class = TeacherSalaryListSerializers

    def delete(self, request, *args, **kwargs):
        list = self.get_object()
        list.deleted = True
        list.save()
        teacher_salary = list.salary_id
        teacher_salary.taken_salary -= list.salary
        teacher_salary.remaining_salary += list.salary
        teacher_salary.save()

        return Response({"detail": "List salary was deleted successfully"}, status=status.HTTP_200_OK)


class TeacherSalaryCreateAPIView(generics.ListCreateAPIView):
    serializer_class = TeacherSalarySerializers

    def get_queryset(self):
        queryset = TeacherSalary.objects.all()
        branch_id = self.request.query_params.get('branch_id', None)
        if branch_id is not None:
            queryset = queryset.filter(branch_id=branch_id)
        return queryset

    def perform_create(self, serializer):
        serializer.save()
