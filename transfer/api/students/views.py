from rest_framework import generics

from students.models import Student, DeletedNewStudent
from .serializers import StudentSerializerTransfer, TransferDeletedNewStudentSerializer
from .serializers import StudentSerializerTransfer, StudentHistoryGroupCreateSerializerTransfer, StudentCharitySerializerTransfer
from students.models import Student, StudentHistoryGroups, StudentCharity


class StudentCreateView(generics.CreateAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentSerializerTransfer


class DeletedStudentCreateView(generics.CreateAPIView):
    queryset = DeletedNewStudent.objects.all()
    serializer_class = TransferDeletedNewStudentSerializer
class StudentHistoryGroupView(generics.CreateAPIView):
    queryset = StudentHistoryGroups.objects.all()
    serializer_class = StudentHistoryGroupCreateSerializerTransfer


class StudentCharityView(generics.CreateAPIView):
    queryset = StudentCharity.objects.all()
    serializer_class = StudentCharitySerializerTransfer
