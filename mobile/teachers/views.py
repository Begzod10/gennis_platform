import calendar
import json
from datetime import datetime

from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from attendances.models import AttendancePerDay, Student, AttendancePerMonth, Group
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
