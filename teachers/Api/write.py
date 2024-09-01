from rest_framework import generics
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from teachers.models import Teacher, TeacherSalaryList, TeacherSalary
from teachers.serializers import (
    TeacherSerializer, TeacherSalaryListCreateSerializers, TeacherSalaryCreateSerializersUpdate
)


class TeacherCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]

    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer


class TeacherUpdateView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]

    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer


class TeacherDestroyView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]

    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer


class TeacherSalaryCreateAPIView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]

    serializer_class = TeacherSalaryListCreateSerializers


class TeacherSalaryDeleteAPIView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]

    queryset = TeacherSalaryList.objects.all()
    serializer_class = TeacherSalaryListCreateSerializers

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.salary_id:
            instance.salary_id.taken_salary -= instance.salary
            instance.salary_id.remaining_salary += instance.salary
            instance.salary_id.save()

        instance.deleted = True
        instance.save()
        return Response({"msg": " salary deleted successfully"}, status=status.HTTP_200_OK)


class TeacherSalaryUpdateAPIView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]

    queryset = TeacherSalaryList.objects.all()
    serializer_class = TeacherSalaryListCreateSerializers


class TeacherSalaryUpdateAPIViewPatch(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]

    queryset = TeacherSalary.objects.all()
    serializer_class = TeacherSalaryCreateSerializersUpdate
