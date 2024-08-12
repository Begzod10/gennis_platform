from rest_framework import generics
from .serializers import StudentSerializerTransfer, StudentHistoryGroupCreateSerializer, StudentCharitySerializer
from students.models import Student, StudentHistoryGroups, StudentCharity


class StudentCreateView(generics.CreateAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentSerializerTransfer


class StudentHistoryGroupView(generics.CreateAPIView):
    queryset = StudentHistoryGroups.objects.all()
    serializer_class = StudentHistoryGroupCreateSerializer


class StudentCharityView(generics.CreateAPIView):
    queryset = StudentCharity.objects.all()
    serializer_class = StudentCharitySerializer
