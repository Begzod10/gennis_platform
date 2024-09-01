from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from teachers.models import TeacherAttendance
from teachers.serializers import TeacherAttendanceSerializers


class TeacherAttendanceCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = TeacherAttendance.objects.all()
    serializer_class = TeacherAttendanceSerializers


class TeacherAttendanceDestroyView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]
    queryset = TeacherAttendance.objects.all()
    serializer_class = TeacherAttendanceSerializers
