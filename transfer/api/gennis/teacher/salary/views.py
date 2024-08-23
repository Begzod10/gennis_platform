from rest_framework import generics

from teachers.models import TeacherSalary, TeacherSalaryList, TeacherBlackSalary
from transfer.api.gennis.teacher.salary.serializers import TransferTeacherSalaryCreateSerializers, \
    TransferTeacherSalaryListCreateSerializers, TransferTeacherBlackSalaryCreateSerializers


class TransferTeacherSalaryCreate(generics.CreateAPIView):
    queryset = TeacherSalary.objects.all()
    serializer_class = TransferTeacherSalaryCreateSerializers


class TransferTeacherSalaryListCreate(generics.CreateAPIView):
    queryset = TeacherSalaryList.objects.all()
    serializer_class = TransferTeacherSalaryListCreateSerializers


class TransferTeacherBlackSalaryCreate(generics.CreateAPIView):
    queryset = TeacherBlackSalary.objects.all()
    serializer_class = TransferTeacherBlackSalaryCreateSerializers
