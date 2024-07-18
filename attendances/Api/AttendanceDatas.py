from rest_framework.views import APIView
from rest_framework.response import Response
from group.models import Group
import jwt
import json
import calendar
from datetime import datetime


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

        years = {attendance.month_date.year for attendance in group.attendance_per_month.all()}
        months = {attendance.month_date.month for attendance in group.attendance_per_month.all()}

        year = today.year
        month = today.month

        days = []
        for time_table in group.grouptimetable_set.all():
            days.extend(self.get_specific_weekdays(year, month, time_table.week.order))

        return Response({
            'years': sorted(years),
            'months': sorted(months),
            'days': sorted(set(days))
        })
