from django.db.models.query import QuerySet
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from rest_framework import generics, filters
from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from branch.models import Branch
from permissions.response import QueryParamFilterMixin
from teachers.models import TeacherGroupStatistics, Teacher, TeacherSalaryList, TeacherSalary, TeacherAttendance
from teachers.serializer.lists import ActiveListTeacherSerializer, TeacherSalaryMonthlyListSerializer, \
    TeacherSalaryForOneMonthListSerializer, calc_teacher_salary
from teachers.serializers import (TeacherSerializerRead, TeacherSalaryListReadSerializers,
                                  TeacherGroupStatisticsReadSerializers, TeacherSalaryReadSerializers)


class TeacherGroupStatisticsListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    # http://ip_adress:8000/Teachers/teacher-statistics-view/?branch_id=3
    queryset = TeacherGroupStatistics.objects.all()
    serializer_class = TeacherGroupStatisticsReadSerializers

    def get_queryset(self):
        branch = self.request.query_params.get('branch_id', None)
        if branch is not None:
            teacher_group_statistics = TeacherGroupStatistics.objects.get(branch=branch)
        else:
            teacher_group_statistics = TeacherGroupStatistics.objects.all()
        return teacher_group_statistics


class TeacherListView(QueryParamFilterMixin, generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    app_name = "O'qtuvchilar"
    filter_mappings = {'branch': "user__branch_id", 'age': 'user__birth_date', "subject": 'subject__id',
        'language': 'user__language_id', 'deleted': 'deleted',

    }
    queryset = Teacher.objects.all()
    serializer_class = ActiveListTeacherSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['user__name', 'user__surname', 'user__username']

    def get_queryset(self):
        queryset = Teacher.objects.all()
        queryset = self.filter_queryset(queryset)
        return queryset


# test
class TeacherRetrieveView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializerRead

    def get(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        data = serializer.data
        if not instance.teacher_salary_type:
            data['msg'] = "O'qituvchiga toifa tanlanmagan"
        return Response(data)


class TeacherSalaryListAPIView(QueryParamFilterMixin, generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    filter_mappings = {'status': 'deleted', 'branch': 'branch', 'teacher_salary': 'salary_id', }
    serializer_class = TeacherSalaryListReadSerializers
    search_fields = ['teacher__user__name', 'teacher__user__surname', 'teacher__user__username']
    filter_backends = [filters.SearchFilter]

    def get_queryset(self):
        queryset = TeacherSalaryList.objects.all()
        return self.filter_queryset(queryset)


class TeacherSalaryDetailAPIView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]

    queryset = TeacherSalary.objects.all()
    serializer_class = TeacherSalaryMonthlyListSerializer

    def retrieve(self, request, *args, **kwargs):

        user_salary_list = self.get_object()

        if isinstance(user_salary_list, QuerySet):
            user_salary_list_data = self.get_serializer(user_salary_list, many=True).data
        else:
            user_salary_list_data = self.get_serializer(user_salary_list).data

        return Response(user_salary_list_data)

    def get_object(self):
        user_id = self.kwargs.get('pk')
        try:
            return TeacherSalary.objects.filter(teacher_id=user_id).all()
        except TeacherSalary.DoesNotExist:
            raise NotFound('TeacherSalary not found for the given teacher_id')


class TeacherSalaryDetailAPIView2(generics.RetrieveAPIView):
    # permission_classes = [IsAuthenticated]

    queryset = TeacherSalary.objects.all()
    serializer_class = TeacherSalaryMonthlyListSerializer

    def retrieve(self, request, *args, **kwargs):

        user_salary_list = self.get_object()

        if isinstance(user_salary_list, QuerySet):
            user_salary_list_data = self.get_serializer(user_salary_list, many=True).data
        else:
            user_salary_list_data = self.get_serializer(user_salary_list).data

        return Response(user_salary_list_data)

    def get_object(self):
        user_id = self.kwargs.get('pk')
        try:
            return TeacherSalary.objects.filter(teacher__user__id=user_id).all()
        except TeacherSalary.DoesNotExist:
            raise NotFound('TeacherSalary not found for the given teacher_id')


class TeacherSalaryListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]

    serializer_class = TeacherSalaryReadSerializers

    def get_queryset(self):
        queryset = TeacherSalary.objects.all()
        branch_id = self.request.query_params.get('branch_id', None)
        if branch_id is not None:
            queryset = queryset.filter(branch_id=branch_id)
        return queryset


class TeacherSalaryListDetailView(QueryParamFilterMixin, generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]

    filter_mappings = {'status': 'deleted'}
    queryset = TeacherSalaryList.objects.all()
    serializer_class = TeacherSalaryForOneMonthListSerializer

    def retrieve(self, request, *args, **kwargs):

        user_salary_list = self.get_object()
        user_salary_list = self.filter_queryset(user_salary_list)

        user_salary_list_data = self.get_serializer(user_salary_list, many=True).data
        return Response(user_salary_list_data)

    def get_object(self):
        user_id = self.kwargs.get('pk')
        try:
            queryset = TeacherSalaryList.objects.filter(salary_id_id=user_id, deleted=False).all()
            sum = 0
            for i in queryset:
                sum += i.salary
            salary = TeacherSalary.objects.filter(id=user_id).first()
            salary.remaining_salary = salary.total_salary - sum
            salary.taken_salary = sum
            salary.save()

            queryset2 = TeacherSalaryList.objects.filter(salary_id_id=user_id).all()

            return queryset2
        except TeacherSalaryList.DoesNotExist:
            raise NotFound('UserSalary not found for the given user_id')


class GetTeacherBalance(APIView):
    def get(self, request, user_id):
        teacher = Teacher.objects.get(user_id=user_id)
        balance = calc_teacher_salary(teacher.id)
        return Response({'balance': balance}, status=status.HTTP_200_OK)


class TeacherSalaryListDetailView2(QueryParamFilterMixin, generics.RetrieveAPIView):
    # permission_classes = [IsAuthenticated]

    filter_mappings = {'status': 'deleted'}
    queryset = TeacherSalaryList.objects.all()
    serializer_class = TeacherSalaryForOneMonthListSerializer

    def retrieve(self, request, *args, **kwargs):

        user_salary_list = self.get_object()
        user_salary_list = self.filter_queryset(user_salary_list)

        user_salary_list_data = self.get_serializer(user_salary_list, many=True).data
        return Response(user_salary_list_data)

    def get_object(self):
        user_id = self.kwargs.get('pk')
        try:
            queryset = TeacherSalaryList.objects.filter(salary_id_id=user_id, deleted=False).all()
            sum = 0
            for i in queryset:
                sum += i.salary
            salary = TeacherSalary.objects.filter(id=user_id).first()
            salary.remaining_salary = salary.total_salary - sum
            salary.taken_salary = sum
            salary.save()

            queryset2 = TeacherSalaryList.objects.filter(salary_id_id=user_id).all()

            return queryset2
        except TeacherSalaryList.DoesNotExist:
            raise NotFound('UserSalary not found for the given user_id')


class TeacherFaceIdView(APIView):
    def post(self, request, *args, **kwargs):
        print(request.data)
        face_id = request.data['id']
        branch_id = request.data['branch_id']
        entry_time = request.data['entry_time']
        leave_time = request.data['leave_time']

        date_obj = parse_datetime(entry_time)

        tz = timezone.get_current_timezone()
        if timezone.is_naive(date_obj):
            date_obj = timezone.make_aware(date_obj, tz)
        else:
            date_obj = date_obj.astimezone(tz)

        branch = Branch.objects.get(branch_id=branch_id)
        teacher = Teacher.objects.get(face_id=face_id, user__branch_id=branch.id)

        teacher_attendance, created = TeacherAttendance.objects.get_or_create(
            teacher=teacher,
            entry_time__date=date_obj.date(),
            defaults={
                'entry_time': date_obj,
                'leave_time': parse_datetime(leave_time) if leave_time else None,
                'status': True,
                'system': branch.location.system
            }
        )

        return Response({'face_id': teacher.face_id}, status=status.HTTP_200_OK)
