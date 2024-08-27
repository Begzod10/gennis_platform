from rest_framework import generics, permissions
from rest_framework.response import Response

from permissions.response import QueryParamFilterMixin, CustomResponseMixin
from mobile.teachers.serializers import TeachersSalariesSerializer, TeacherSalary, TeachersDebtedStudents, Teacher, \
    TeacherProfileSerializer


class TeacherPaymentsListView(generics.ListAPIView, QueryParamFilterMixin, CustomResponseMixin):
    permission_classes = [permissions.IsAuthenticated]

    queryset = TeacherSalary.objects.all()
    serializer_class = TeachersSalariesSerializer
    filter_mappings = {
        'month': 'month_date__month',
        'year': 'month_date__year',
    }

    def get(self, request, *args, **kwargs):
        queryset = TeacherSalary.objects.all()

        queryset = self.filter_queryset(queryset)
        serializer = TeachersSalariesSerializer(queryset, many=True)
        return Response(serializer.data)


class TeachersDebtedStudentsListView(generics.ListAPIView, QueryParamFilterMixin, CustomResponseMixin):
    permission_classes = [permissions.IsAuthenticated]

    queryset = Teacher.objects.all()
    serializer_class = TeachersDebtedStudents
    filter_mappings = {
        'group': 'group__id',
    }

    def get(self, request, *args, **kwargs):
        queryset = Teacher.objects.all()

        queryset = self.filter_queryset(queryset)
        serializer = TeachersDebtedStudents(queryset, many=True)
        return Response(serializer.data)


class TeacherProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]

    queryset = Teacher.objects.all()
    serializer_class = TeacherProfileSerializer
