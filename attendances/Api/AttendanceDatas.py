import calendar
import json
from datetime import datetime

from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework.views import APIView

from group.models import Group
from ..models import AttendancePerMonth


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

    def get(self, request, group_id):
        group = Group.objects.get(pk=group_id)
        attendance_records = AttendancePerMonth.objects.filter(group=group)

        year_month_days = {}

        for record in attendance_records:
            year = record.month_date.year
            month = record.month_date.month
            days = []

            for time_table in group.group_time_table.all():
                days.extend(self.get_specific_weekdays(year, month, time_table.week.order))

            if year not in year_month_days:
                year_month_days[year] = {}
            if month not in year_month_days[year]:
                year_month_days[year][month] = sorted(set(days))

        final_output = {year: sorted(year_month_days[year].keys()) for year in year_month_days}

        return JsonResponse(final_output)
