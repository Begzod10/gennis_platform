from rest_framework import generics
from teachers.models import TeacherAttendance, Teacher
from teachers.serializers import TeacherAttendanceListSerializers, TeacherSerializer, TeacherSerializerRead
from user.functions.functions import check_auth
from rest_framework.response import Response
from permissions.functions.CheckUserPermissions import check_user_permissions


class TeacherAttendanceListView(generics.ListAPIView):
    queryset = TeacherAttendance.objects.all()
    serializer_class = TeacherAttendanceListSerializers

    def get(self, request, *args, **kwargs):
        user, auth_error = check_auth(request)
        if auth_error:
            return Response(auth_error)

        table_names = ['teacherattendance', 'teacher', 'system']
        permissions = check_user_permissions(user, table_names)

        queryset = TeacherAttendance.objects.all()
        serializer = TeacherAttendanceListSerializers(queryset, many=True)
        return Response({'teacherattendances': serializer.data, 'permissions': permissions})


class TeacherAttendanceRetrieveView(generics.RetrieveAPIView):
    queryset = TeacherAttendance.objects.all()
    serializer_class = TeacherAttendanceListSerializers

    def retrieve(self, request, *args, **kwargs):
        user, auth_error = check_auth(request)
        if auth_error:
            return Response(auth_error)

        table_names = ['teacherattendance', 'teacher', 'system']
        permissions = check_user_permissions(user, table_names)
        teacher_attendance = self.get_object()
        teacher_attendance_data = self.get_serializer(teacher_attendance).data
        return Response({'teacherattendance': teacher_attendance_data, 'permissions': permissions})


class TeachersForBranches(generics.ListAPIView):
    serializer_class = TeacherSerializerRead

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        return Teacher.objects.filter(branches__in=[pk])


class TeachersForSubject(generics.ListAPIView):
    serializer_class = TeacherSerializerRead

    def get_queryset(self):
        branch_id = self.kwargs.get('branch_id')
        subject_id = self.kwargs.get('subject_id')
        print(branch_id, subject_id)
        return Teacher.objects.filter(branches__in=[branch_id], subject__in=[subject_id])

# class SchoolTeachers(generics.ListAPIView):
#     queryset = Teacher.objects.filter(user)
