from rest_framework import generics, status
from rest_framework.response import Response

from teachers.models import Teacher, TeacherSalaryList
from teachers.serializers import (
    TeacherSerializer, TeacherSalaryListCreateSerializers, TeacherSalaryCreateSerializers
)


class TeacherCreateView(generics.CreateAPIView):
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer


class TeacherUpdateView(generics.UpdateAPIView):
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer


class TeacherDestroyView(generics.DestroyAPIView):
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer


class TeacherSalaryCreateAPIView(generics.CreateAPIView):
    serializer_class = TeacherSalaryListCreateSerializers

    def perform_create(self, serializer):
        serializer.save()


class TeacherSalaryDeleteAPIView(generics.DestroyAPIView):
    queryset = TeacherSalaryList.objects.all()
    serializer_class = TeacherSalaryListCreateSerializers

    def delete(self, request, *args, **kwargs):
        list = self.get_object()
        list.deleted = True
        list.save()
        teacher_salary = list.salary_id
        teacher_salary.taken_salary -= list.salary
        teacher_salary.remaining_salary += list.salary
        teacher_salary.save()

        return Response({"detail": "List salary was deleted successfully"}, status=status.HTTP_200_OK)


class TeacherSalaryUpdateAPIView(generics.UpdateAPIView):
    queryset = TeacherSalaryList.objects.all()
    serializer_class = TeacherSalaryListCreateSerializers


class TeacherSalaryCreateAPIView(generics.CreateAPIView):
    serializer_class = TeacherSalaryCreateSerializers

    def perform_create(self, serializer):
        serializer.save()
