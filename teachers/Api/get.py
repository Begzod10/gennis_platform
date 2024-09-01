from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from teachers.models import TeacherAttendance, Teacher
from teachers.serializers import TeacherAttendanceListSerializers, TeacherSerializerRead


class TeacherAttendanceListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = TeacherAttendance.objects.all()
    serializer_class = TeacherAttendanceListSerializers

    def get(self, request, *args, **kwargs):
        queryset = TeacherAttendance.objects.all()

        serializer = TeacherAttendanceListSerializers(queryset, many=True)
        return Response(serializer.data)


class TeacherAttendanceRetrieveView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    queryset = TeacherAttendance.objects.all()
    serializer_class = TeacherAttendanceListSerializers

    def retrieve(self, request, *args, **kwargs):
        teacher_attendance = self.get_object()
        teacher_attendance_data = self.get_serializer(teacher_attendance).data
        return Response(teacher_attendance_data)


class TeachersForBranches(generics.ListAPIView):
    permission_classes = [IsAuthenticated]

    serializer_class = TeacherSerializerRead

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        return Teacher.objects.filter(branches__in=[pk])


class TeachersForSubject(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TeacherSerializerRead

    def get_queryset(self):
        branch_id = self.request.query_params.get('branch')
        subject_id = self.request.query_params.get('subject')
        return Teacher.objects.filter(branches__in=[branch_id], subject__in=[subject_id])
