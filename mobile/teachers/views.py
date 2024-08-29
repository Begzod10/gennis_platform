from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions

from mobile.teachers.serializers import TeachersSalariesSerializer, TeachersDebtedStudents, Teacher, \
    TeacherProfileSerializer, AttendancesTodayStudentsSerializer, GroupListSeriliazersMobile
from permissions.response import QueryParamFilterMixin, CustomResponseMixin, CustomUser
from ..get_user import get_user


class TeacherPaymentsListView(CustomResponseMixin, QueryParamFilterMixin, generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = TeachersSalariesSerializer
    filter_mappings = {
        'month': 'month_date__month',
        'year': 'month_date__year',
    }

    def get_queryset(self):
        user = self.request.user
        teacher = get_object_or_404(Teacher, user_id=user.id)
        return teacher.teacher_id_salary.all().distinct()


class TeachersDebtedStudentsListView(QueryParamFilterMixin, CustomResponseMixin, generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]

    queryset = Teacher.objects.all()
    serializer_class = TeachersDebtedStudents
    filter_mappings = {
        'group': 'id',
    }

    def get_queryset(self):
        user = self.request.user
        teacher = get_object_or_404(Teacher, user_id=user.id)
        return teacher.group_set.all().distinct()


class TeacherProfileView(QueryParamFilterMixin, CustomResponseMixin, generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Teacher.objects.all()
    serializer_class = TeacherProfileSerializer

    def get_object(self):
        user = get_user(self.request)
        user = CustomUser.objects.get(pk=user)
        user = user.id
        return user


class TeachersAttendaceStudentsListView(QueryParamFilterMixin, CustomResponseMixin, generics.ListAPIView):
    # filter_mappings = {
    #     'group': 'id',
    # }

    permission_classes = [permissions.IsAuthenticated]

    queryset = Teacher.objects.all()
    serializer_class = AttendancesTodayStudentsSerializer

    def get_queryset(self):
        user = self.request.user
        teacher = get_object_or_404(Teacher, user_id=user.id)
        return teacher.group_set.all().distinct()


class GroupListView(QueryParamFilterMixin, CustomResponseMixin, generics.ListAPIView):
    # filter_mappings = {
    #     'group': 'id',
    # }

    permission_classes = [permissions.IsAuthenticated]

    queryset = Teacher.objects.all()
    serializer_class = GroupListSeriliazersMobile

    def get_queryset(self):
        user = self.request.user
        teacher = get_object_or_404(Teacher, user_id=user.id)
        return teacher.group_set.all().distinct()
