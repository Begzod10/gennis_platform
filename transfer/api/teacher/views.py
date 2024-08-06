from rest_framework import generics

from teachers.models import Teacher
from transfer.api.teacher.serializers import (
    TeacherSerializerTransfer
)


class TeacherCreateView(generics.CreateAPIView):
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializerTransfer
