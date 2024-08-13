from rest_framework import generics

from students.models import Student, DeletedNewStudent
from .serializers import StudentSerializerTransfer, TransferDeletedNewStudentSerializer


class StudentCreateView(generics.CreateAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentSerializerTransfer


class DeletedStudentCreateView(generics.CreateAPIView):
    queryset = DeletedNewStudent.objects.all()
    serializer_class = TransferDeletedNewStudentSerializer
