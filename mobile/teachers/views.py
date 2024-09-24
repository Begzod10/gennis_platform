import calendar
import json
from datetime import datetime

from django.db.models.functions import ExtractMonth, ExtractYear
from django.shortcuts import get_object_or_404
from rest_framework import permissions, generics
from rest_framework.response import Response
from rest_framework.views import APIView

from attendances.models import AttendancePerDay, Student, AttendancePerMonth, Group
from mobile.teachers.serializers import TeachersDebtedStudents, TeacherProfileSerializer, \
    AttendancesTodayStudentsSerializer, GroupListSeriliazersMobile
from permissions.response import QueryParamFilterMixin
from teachers.models import Teacher, TeacherSalary
from user.models import CustomUser
from .serializers import TeachersSalariesSerializer
from ..get_user import get_user


class TeacherPaymentsListView(QueryParamFilterMixin, generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = TeachersSalariesSerializer
    filter_mappings = {
        'month': 'month_date__month',
        'year': 'month_date__year',
    }

    def get(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        teacher_salaries_data = serializer.data

        def get_datas():
            current_year = datetime.now().year
            current_month = datetime.now().month

            unique_dates = TeacherSalary.objects.annotate(
                year=ExtractYear('month_date'),
                month=ExtractMonth('month_date')
            ).filter(teacher__user=self.request.user).values('year', 'month').distinct().order_by('year', 'month')

            year_month_dict = {}
            for date in unique_dates:
                year = date['year']
                month = date['month']
                if year not in year_month_dict:
                    year_month_dict[year] = []
                year_month_dict[year].append(
                  month,
                )

            year_month_list = [{'year': year, 'months': months} for year, months in year_month_dict.items()]

            return year_month_list

        combined_data = {
            'salaries': teacher_salaries_data,
            'dates': get_datas()
        }

        return Response(combined_data)

    def get_queryset(self):
        user = self.request.user
        teacher = get_object_or_404(Teacher, user=user)
        return teacher.teacher_id_salary.all().distinct()


class TeachersDebtedStudentsListView(QueryParamFilterMixin, generics.ListAPIView):
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


class TeacherProfileView(QueryParamFilterMixin, generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Teacher.objects.all()
    serializer_class = TeacherProfileSerializer

    def get_object(self):
        user = get_user(self.request)
        user = CustomUser.objects.get(pk=user)
        user = user.id
        return user


class TeachersAttendaceStudentsListView(QueryParamFilterMixin, generics.ListAPIView):
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


class GroupListView(QueryParamFilterMixin, generics.ListAPIView):
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


class AttendanceListMobile(QueryParamFilterMixin, APIView):
    filter_mappings = {
        'group': 'id'

    }

    def get_attendances_json(self, groups, month_date, student_id):
        attendances_json = []

        for group in groups:
            attendances = AttendancePerDay.objects.filter(
                group=group,
                day__month=month_date.month,
                student__id=student_id
            ).distinct()

            days = sorted(set(attendance.day.day for attendance in attendances))
            group_attendances = []

            for attendance in attendances:
                day = attendance.day.day
                group_attendances.append({
                    "day": day,
                    'status': attendance.status,
                    'name': attendance.student.user.name,
                    'surname': attendance.student.user.surname
                })

            attendances_json.append({'name': group.name, 'days': group_attendances})  # Group nomi bo'yicha key yaratish

        return attendances_json

    def post(self, request, student_id):
        data = json.loads(request.body)
        month_date = datetime(data['year'], data['month'], 1)
        student = Student.objects.get(pk=student_id)
        groups = student.groups_student.all()
        groups = self.filter_queryset(groups)
        attendances_json = self.get_attendances_json(groups, month_date, student_id)
        return Response({'students': attendances_json})

    def get(self, request, student_id):
        today = datetime.today()
        month_date = datetime(today.year, today.month, 1)
        student = Student.objects.get(pk=student_id)
        groups = student.groups_student.all()
        groups = self.filter_queryset(groups)

        attendances_json = self.get_attendances_json(groups, month_date, student_id)
        return Response({'students': attendances_json})


class AttendanceListMobile(QueryParamFilterMixin, APIView):
    filter_mappings = {
        'group': 'id'

    }

    def get_specific_weekdays(self, year, month, weekday):
        c = calendar.Calendar()
        return [date.day for date in c.itermonthdates(year, month) if date.month == month and date.weekday() == weekday]

    def get_attendance_days(self, groups, year, month, student_id=None):
        days = []
        for group in groups:
            for time_table in group.group_time_table.all():
                specific_days = self.get_specific_weekdays(year, month, time_table.week.order)
                if student_id:
                    specific_days = [day for day in specific_days if AttendancePerMonth.objects.filter(
                        group=group, month_date__day=day, student__id=student_id).exists()]
                days.extend(specific_days)
        return sorted(set(days))

    def post(self, request, student_id):
        try:
            data = json.loads(request.body)
            year = data['year']
            month = data['month']
            student = Student.objects.get(pk=student_id)
            groups = student.groups_student.all()
            groups = self.filter_queryset(groups)

            days = self.get_attendance_days(groups, year, month, student_id)
            return Response({'days': days})
        except Student.DoesNotExist:
            return Response({'error': 'Student not found'}, status=404)
        except KeyError as e:
            return Response({'error': f'Missing key in request: {str(e)}'}, status=400)

    def get(self, request, student_id):
        try:
            student = Student.objects.get(pk=student_id)
            groups = student.groups_student.all()
            groups = self.filter_queryset(groups)

            attendance_records = AttendancePerMonth.objects.filter(group__in=groups)
            if student_id:
                attendance_records = attendance_records.filter(student__id=student_id)

            year_month_days = {}
            for record in attendance_records:
                year = record.month_date.year
                month = record.month_date.month

                if year not in year_month_days:
                    year_month_days[year] = {}

                if month not in year_month_days[year]:
                    year_month_days[year][month] = self.get_attendance_days(groups, year, month, student_id)

            final_output = {year: sorted(year_month_days[year].keys()) for year in year_month_days}
            return Response(final_output)
        except Student.DoesNotExist:
            return Response({'error': 'Student not found'}, status=404)


class MobileGroupTime(QueryParamFilterMixin, APIView):
    filter_mappings = {
        'group': 'id'
    }

    def get(self, request):
        try:
            groups = Group.objects.all()
            groups = self.filter_queryset(groups)
            data = []
            for group in groups:
                for time_table in group.group_time_table.all():
                    data.append({
                        'id': time_table.id,
                        'week': time_table.week.name,
                        'start': time_table.start_time.strftime('%H:%M'),
                        'end': time_table.end_time.strftime('%H:%M')
                    })
            return Response(data)
        except Group.DoesNotExist:
            return Group({'error': 'Group not found'}, status=404)
