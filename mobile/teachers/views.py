import calendar
import json
from datetime import datetime

from django.db.models.functions import ExtractMonth, ExtractYear
from django.shortcuts import get_object_or_404
from rest_framework import permissions, generics
from rest_framework.response import Response
from rest_framework.views import APIView

from attendances.models import AttendancePerDay, Student, AttendancePerMonth, Group, StudentScoreByTeacher
from time_table.models import GroupTimeTable
from permissions.response import QueryParamFilterMixin
from teachers.models import Teacher, TeacherSalary
from user.models import CustomUser
from school_time_table.models import ClassTimeTable
from ..get_user import get_user

from django.utils import timezone
from datetime import timedelta


class TeacherGroupProfileView(APIView):
    def get(self, request):
        group_id = request.query_params.get('group_id')
        group = Group.objects.get(pk=group_id)
        month = datetime.now().month
        year = datetime.now().year
        # Get current week's Monday and Friday
        today = timezone.now().date()
        monday = today - timedelta(days=today.weekday())  # Start of week (Monday)
        friday = monday + timedelta(days=4)  # End of work week (Friday)

        # Filter ClassTimeTable for current week and group
        class_schedule = ClassTimeTable.objects.filter(
            group_id=group_id,
            date__gte=monday,
            date__lte=friday
        ).select_related('week', 'room', 'hours', 'teacher', 'subject').order_by('date', 'hours')
        next_lesson = ClassTimeTable.objects.filter(
            group_id=group_id,
            date__gt=datetime.now().date(),
        ).first()
        teacher = group.teacher.first()
        info = {
            "group_name": f"{group.class_number.number}-{group.color.name}",
            "group_id": group.id,
            "students_count": group.students.count(),
            "next_lesson": next_lesson.date.strftime('%Y-%m-%d') if next_lesson else None,
            "start_time": next_lesson.hours.start_time.strftime('%H:%M') if next_lesson else None,
            "students": [],
            "schedule": []
        }

        for student in group.students.all():
            student_attendance = StudentScoreByTeacher.objects.filter(
                student=student,
                teacher=teacher,
                group=group,
                day__month=month,
                day__year=year
            ).all()
            total_average = round(sum(score.average for score in student_attendance) / len(student_attendance)) if student_attendance else 0
            total_persent = student_attendance = StudentScoreByTeacher.objects.filter(
                student=student,
                teacher=teacher,
                group=group,
                status=True,
                day__month=month,
                day__year=year
            ).count()
            present_percent = round(total_persent / student_attendance * 100, 2) if student_attendance else 0
            info['students'].append({
                'id': student.id,
                'name': student.user.name,
                'surname': student.user.surname,
                'average': total_average,
                'present_percent': present_percent
            })
        for schedule in class_schedule:
            info['schedule'].append({
                'date': schedule.date,
                'week_day': schedule.week.name_en if schedule.week else None,
                'room': schedule.room.name if schedule.room else None,
                'time': f"{schedule.hours.start_time} - {schedule.hours.end_time}",
                'subject': schedule.subject.name if schedule.subject else None,
            })

        return Response(info)
