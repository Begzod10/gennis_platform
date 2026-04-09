from datetime import datetime
from rest_framework.views import APIView
from rest_framework.response import Response
from group.models import Group
import jwt
import json
from ..models import AttendancePerDay
from teachers.models import Teacher
from .functions.CalculateGroupOverallAttendance import calculate_group_attendances
from rest_framework.permissions import IsAuthenticated


class AttendanceDelete(APIView):
    permission_classes = [IsAuthenticated]

    def get_attendances_json(self, group, month_date):
        attendances = group.attendance_per_day.filter(group__attendance_per_month__month_date=month_date).distinct()
        days = sorted(set(attendance.day.day for attendance in attendances))
        attendances_json = {day: [] for day in days}

        for attendance in attendances:
            day = attendance.day.day
            attendances_json[day].append({
                'id': attendance.id,
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

    def delete(self, request, group_id):
        data = json.loads(request.body)
        attendance_per_day = AttendancePerDay.objects.get(pk=data['id'])
        attendance_per_month = attendance_per_day.attendance_per_month
        attendance_per_day.delete()
        salary_attendance_per_month = 0
        debt_attendance_per_month = 0
        charity_per_day = 0
        for per_day in attendance_per_month.attendanceperday_set.all():
            salary_attendance_per_month += per_day.salary_per_day
            debt_attendance_per_month += per_day.debt_per_day
            charity_per_day += per_day.charity_per_day
        attendance_per_month.total_salary = salary_attendance_per_month
        attendance_per_month.total_debt = debt_attendance_per_month
        attendance_per_month.total_charity = charity_per_day
        attendance_per_month.save()
        teacher = Teacher.objects.get(pk=attendance_per_month.teacher_id)
        overall_teacher_attendance_per_month = teacher.attendance_per_month.filter(
            month_date=attendance_per_month.month_date)
        overall_teacher_salary = 0
        for per_month in overall_teacher_attendance_per_month:
            overall_teacher_salary += per_month.total_salary
        teacher_salary = teacher.teacher_id_salary.get(month_date=attendance_per_month.month_date)
        teacher_salary.total_salary = overall_teacher_salary
        teacher_salary.save()
        calculate_group_attendances(group_id, attendance_per_month.month_date)
        return Response({'msg': "davomat muvaffaqqiyatli o'chirildi"})
