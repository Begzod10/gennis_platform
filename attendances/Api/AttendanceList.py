import json
from collections import defaultdict
from datetime import datetime

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from group.models import Group
from user.models import CustomUser
from ..models import AttendancePerDay, Student


class AttendanceList(APIView):
    permission_classes = [IsAuthenticated]

    def get_attendances_json(self, group, month_date, student_id):
        attendances = AttendancePerDay.objects.filter(group=group, day__month=month_date.month,
                                                      student__id=student_id).distinct()

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

    def post(self, request, group_id, student_id=None):
        data = json.loads(request.body)
        student_id = request.GET.get('student_id', student_id)  # URL parametrdan student_id ni olish
        month_date = datetime(data['year'], data['month'], 1)
        group = Group.objects.get(pk=group_id)
        attendances_json = self.get_attendances_json(group, month_date, student_id)
        return Response({'students': attendances_json})

    def get(self, request, group_id, student_id=None):
        student_id = request.GET.get('student_id', student_id)  # URL parametrdan student_id ni olish
        today = datetime.today()
        month_date = datetime(today.year, today.month, 1)
        group = Group.objects.get(pk=group_id)
        attendances_json = self.get_attendances_json(group, month_date, student_id)
        return Response({'students': attendances_json})


class AttendanceListForAllGroups(APIView):
    permission_classes = [IsAuthenticated]

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

        attendances_json = self.get_attendances_json(groups, month_date, student_id)
        return Response({'students': attendances_json})

    def get(self, request, student_id):
        today = datetime.today()
        month_date = datetime(today.year, today.month, 1)
        student = Student.objects.get(pk=student_id)
        groups = student.groups_student.all()  # Studentning barcha guruhlarini olish

        attendances_json = self.get_attendances_json(groups, month_date, student_id)
        return Response({'students': attendances_json})


class AttendanceListSchool(APIView):
    # permission_classes = [IsAuthenticated]

    def get_attendances_json(self, group, month_date):
        attendances = AttendancePerDay.objects.filter(group=group, day__month=month_date.month).distinct()
        year_month_data = defaultdict(set)
        attendance_data = AttendancePerDay.objects.filter(group=group).order_by('day').distinct()
        for attendance in attendance_data:
            year = attendance.day.year
            month = attendance.day.month
            year_month_data[year].add(month)
        year_month_result = [
            {
                'year': year,
                'month': sorted(list(months))
            } for year, months in year_month_data.items()
        ]

        days = sorted(set(attendance.day.day for attendance in attendances))
        attendances_json = {
            'students': [],
            'days': days,
            "years": year_month_result

        }

        for student in group.students.all():
            student_data = {
                'name': student.user.name,
                'surname': student.user.surname,
                'days': []
            }

            attendances_student = AttendancePerDay.objects.filter(group=group, student=student,
                                                                  day__month=month_date.month).order_by(
                'day').distinct()
            for i in days:
                attendance = attendances_student.filter(day__day=i).first()

                if attendance:
                    student_data['days'].append({
                        'status': attendance.status,
                        'day': i,
                        'reason': attendance.reason
                    })
                else:
                    student_data['days'].append({
                        'status': '',
                        'day': i
                    })

            attendances_json['students'].append(student_data)

        return attendances_json

    def post(self, request, group_id):
        data = json.loads(request.body)
        month_date = datetime(int(data['year']), int(data['month']), 1)
        group = Group.objects.get(pk=group_id)
        attendances_json = self.get_attendances_json(group, month_date)
        return Response({'students': attendances_json})

    def get(self, request, group_id):
        today = datetime.today()
        month_date = datetime(today.year, today.month, 1)
        group = Group.objects.get(pk=group_id)
        attendances_json = self.get_attendances_json(group, month_date)
        return Response({'students': attendances_json})
