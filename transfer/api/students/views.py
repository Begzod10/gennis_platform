from rest_framework import generics
from .serializers import StudentSerializerTransfer
from students.models import Student


class StudentCreateView(generics.CreateAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentSerializerTransfer

