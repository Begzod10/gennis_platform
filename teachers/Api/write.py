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


class TeacherSalaryDeleteAPIView(generics.DestroyAPIView):
    queryset = TeacherSalaryList.objects.all()
    serializer_class = TeacherSalaryListCreateSerializers


class TeacherSalaryUpdateAPIView(generics.UpdateAPIView):
    queryset = TeacherSalaryList.objects.all()
    serializer_class = TeacherSalaryListCreateSerializers
