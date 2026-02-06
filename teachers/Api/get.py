from django.utils import timezone
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from permissions.response import QueryParamFilterMixin
from teachers.models import TeacherAttendance, Teacher, TeacherSalaryType
from teachers.serializers import TeacherAttendanceListSerializers, TeacherSerializerRead, \
    TeacherSalaryTypeSerializerRead
from teachers.serializer.lists import ActiveListTeacherSerializerTime
from teachers.services.teacher_rating import CATEGORY_MAP


class TeacherAttendanceListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = TeacherAttendance.objects.all()
    serializer_class = TeacherAttendanceListSerializers

    def get(self, request, *args, **kwargs):
        queryset = TeacherAttendance.objects.all()

        serializer = TeacherAttendanceListSerializers(queryset, many=True)
        return Response(serializer.data)


class TeacherAttendanceRetrieveView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TeacherAttendanceListSerializers

    def get_queryset(self):
        teacher_id = self.kwargs['pk']

        today = timezone.now().date()

        year = self.request.query_params.get('year', today.year)
        month = self.request.query_params.get('month', today.month)
        day = self.request.query_params.get('day')

        qs = TeacherAttendance.objects.filter(
            teacher_id=teacher_id,
            day__year=year,
            day__month=month
        )

        if day:
            qs = qs.filter(day__day=day)

        return qs


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


class TeachersForSubjectForTimeTable(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ActiveListTeacherSerializerTime

    def get_queryset(self):
        branch_id = self.request.query_params.get('branch')
        subject_id = self.request.query_params.get('subject')

        return Teacher.objects.filter(branches__in=[branch_id], subject__in=[subject_id]).all()


class SalaryType(QueryParamFilterMixin, generics.ListCreateAPIView):
    filter_mappings = {
        'branch': 'branch_id',
    }
    serializer_class = TeacherSalaryTypeSerializerRead
    queryset = TeacherSalaryType.objects.all()


class TeacherRatingAPIView(APIView):

    def get(self, request):
        branch_id = request.query_params.get('branch')
        category = request.query_params.get('category')
        year = request.query_params.get('year')
        month = request.query_params.get('month')
        year = int(year) if year else None
        month = int(month) if month else None

        if category not in CATEGORY_MAP:
            return Response({"detail": "Invalid category"}, status=400)

        data = CATEGORY_MAP[category](branch_id, year, month)

        return Response(data)
