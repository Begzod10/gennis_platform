import calendar
import json
from datetime import datetime

from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework.views import APIView

from group.models import Group
from ..models import AttendancePerMonth, Student


class AttendanceDatas(APIView):
    def get_specific_weekdays(self, year, month, weekday):
        c = calendar.Calendar()
        return [date.day for date in c.itermonthdates(year, month) if date.month == month and date.weekday() == weekday]

    def post(self, request, group_id):
        data = json.loads(request.body)
        group = Group.objects.get(pk=group_id)
        year = data['year']
        month = data['month']

        days = []
        for time_table in group.grouptimetable_set.all():
            days.extend(self.get_specific_weekdays(year, month, time_table.week.order))

        return Response({'days': sorted(set(days))})

    def get(self, request, group_id):
        today = datetime.today()
        group = Group.objects.get(pk=group_id)
        attendance_records = AttendancePerMonth.objects.filter(group=group)
        print(f"Attendance records for group {group_id}: {attendance_records}")

        years = {attendance.month_date.year for attendance in attendance_records}
        months = {attendance.month_date.month for attendance in attendance_records}
        print(attendance_records)

        year = today.year
        month = today.month

        days = []
        for time_table in group.group_time_table.all():  # 'grouptimetable_set' o'rniga 'group_time_table' chaqirilyapti
            days.extend(self.get_specific_weekdays(year, month, time_table.week.order))

        return Response({
            'years': sorted(years),
            'months': sorted(months),
            'days': sorted(set(days))
        })


class AttendanceDatasForGroup(APIView):
    def get_specific_weekdays(self, year, month, weekday):
        c = calendar.Calendar()
        return [date.day for date in c.itermonthdates(year, month) if date.month == month and date.weekday() == weekday]

    def post(self, request, group_id):
        data = json.loads(request.body)
        group = Group.objects.get(pk=group_id)
        year = data['year']
        month = data['month']
        student_id = data.get('student_id')

        days = []
        for time_table in group.grouptimetable_set.all():
            days.extend(self.get_specific_weekdays(year, month, time_table.week.order))

        if student_id:
            days = [day for day in days if AttendancePerMonth.objects.filter(group=group, month_date__day=day,
                                                                             student__id=student_id).exists()]

        return Response({'days': sorted(set(days))})

    def get(self, request, group_id):
        group = Group.objects.get(pk=group_id)
        student_id = request.query_params.get('student_id')

        attendance_records = AttendancePerMonth.objects.filter(group=group)
        if student_id:
            attendance_records = attendance_records.filter(student__id=student_id)

        year_month_days = {}

        for record in attendance_records:
            year = record.month_date.year
            month = record.month_date.month
            days = []

            for time_table in group.group_time_table.all():
                days.extend(self.get_specific_weekdays(year, month, time_table.week.order))

            days = sorted(set(days))
            if year not in year_month_days:
                year_month_days[year] = {}
            if month not in year_month_days[year]:
                year_month_days[year][month] = days

        final_output = {year: sorted(year_month_days[year].keys()) for year in year_month_days}

        return JsonResponse(final_output)

class AttendanceDatasForAllGroup(APIView):
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
            return JsonResponse(final_output)
        except Student.DoesNotExist:
            return JsonResponse({'error': 'Student not found'}, status=404)