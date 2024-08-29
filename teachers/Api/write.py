from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from teachers.models import Teacher, TeacherSalaryList
from teachers.serializers import (
    TeacherSerializer, TeacherSalaryListCreateSerializers
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
    queryset = TeacherSalaryList.objects.all()
    serializer_class = TeacherSalaryListCreateSerializers
class TeacherSalaryUpdateAPIViewPatch(generics.UpdateAPIView):
    queryset = TeacherSalaryList.objects.all()
    serializer_class = TeacherSalaryListCreateSerializers
