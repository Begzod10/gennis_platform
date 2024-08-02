from rest_framework import generics
from teachers.models import TeacherAttendance
from teachers.serializers import TeacherAttendanceSerializers


class TeacherAttendanceCreateView(generics.CreateAPIView):
    queryset = TeacherAttendance.objects.all()
    serializer_class = TeacherAttendanceSerializers


class TeacherAttendanceDestroyView(generics.DestroyAPIView):
    queryset = TeacherAttendance.objects.all()
    serializer_class = TeacherAttendanceSerializers
