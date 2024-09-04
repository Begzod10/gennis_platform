from rest_framework import generics
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from teachers.models import Teacher, TeacherSalaryList, TeacherSalary
from teachers.serializers import (
    TeacherSerializer, TeacherSalaryListCreateSerializers, TeacherSalaryCreateSerializersUpdate
)
from user.models import CustomUser


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


class UploadFile(APIView):
    def post(self, request, *args, **kwargs):
        file = request.FILES.get('file')
        username = self.request.query_params.get('username')
        CustomUser.objects.filter(username=username).update(file=file)
        print(file)
        return Response({"msg": "File uploaded successfully"}, status=status.HTTP_200_OK)
