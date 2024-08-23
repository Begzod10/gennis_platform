import json
from datetime import datetime

from rest_framework.response import Response
from rest_framework.views import APIView

from group.models import Group
from ..models import AttendancePerDay

class AttendanceList(APIView):

    def get_attendances_json(self, group, month_date):
        # attendances = group.attendance_per_day.filter(group__attendance_per_month__month_date=month_date).distinct()
        attendances = AttendancePerDay.objects.filter(group=group, day__month=month_date.month).distinct()

        days = sorted(set(attendance.day.day for attendance in attendances))
        attendances_json = {day: [] for day in days}

        for attendance in attendances:
            day = attendance.day.day
            attendances_json[day].append({
                'status': attendance.status,
                'name': attendance.student.user.name,
                'surname': attendance.student.user.surname
            })

        return attendances_json

    def post(self, request, group_id):
        data = json.loads(request.body)
        month_date = datetime(data['year'], data['month'], 1)
        group = Group.objects.get(pk=group_id)
        attendances_json = self.get_attendances_json(group, month_date)
        return Response({'students': attendances_json})

    def get(self, request, group_id):
        today = datetime.today()
        month_date = datetime(today.year, today.month, 1)
        group = Group.objects.get(pk=group_id)
        attendances_json = self.get_attendances_json(group, month_date)
        return Response({'students': attendances_json})
