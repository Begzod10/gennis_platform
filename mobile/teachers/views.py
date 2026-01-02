import calendar
import json
from datetime import datetime
from teachers.serializers import TeacherSalaryList
from django.db.models.functions import ExtractMonth, ExtractYear
from django.shortcuts import get_object_or_404
from rest_framework import permissions, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from group.models import GroupSubjects
from attendances.models import AttendancePerDay, Student, AttendancePerMonth, Group, StudentScoreByTeacher
from time_table.models import GroupTimeTable
from permissions.response import QueryParamFilterMixin
from teachers.models import Teacher, TeacherSalary
from user.models import CustomUser
from flows.models import Flow
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
            total_average = round(sum(score.average for score in student_attendance) / len(
                student_attendance)) if student_attendance else 0
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


class TeacherProfileView(APIView):
    def get(self, request):
        teacher_id = request.query_params.get('teacher_id')
        teacher = Teacher.objects.get(pk=teacher_id)
        teacher_salary = TeacherSalary.objects.filter(teacher=teacher).last()
        self.class_room = True
        user = teacher.user
        info = {
            'id': user.id,
            'name': user.name,
            'surname': user.surname,
            'username': user.username,
            'father_name': user.father_name,
            'balance': teacher_salary.remaining_salary if teacher_salary.remaining_salary else teacher_salary.total_salary,
            "teacher_id": teacher.id,
            'role': 'teacher',
            'birth_date': user.birth_date.isoformat() if user.birth_date else None,
            'phone_number': user.phone,
            'branch_id': user.branch_id,
            'observer': user.observer,
            'subjects': [{
                'id': subject.id,
                'name': subject.name
            } for subject in teacher.subject.all()],
            'color': teacher.color if teacher.color else None,
            'groups': [{
                'name': group.name if group.name else f'{group.class_number.number}-{group.color.name}',
                'id': group.id,
                'subjects': [
                    {'id': subject.subject.id, 'name': subject.subject.name} for subject in
                    GroupSubjects.objects.filter(group=group).all()
                ],
                'teacher_salary': group.teacher_salary,
                'price': group.price,
                "teacher_id": user.id
            } for group in teacher.group_set.all()],
            'flows': [
                {
                    'id': flow.id,
                    'name': flow.name,
                    'subject': {
                        'id': flow.subject.id if flow.subject else None,
                        'name': flow.subject.name if flow.subject else None,
                    } if flow.subject else None,
                    'branch': {
                        'id': flow.branch.id,
                        'name': flow.branch.name,
                    } if flow.branch else None,
                    'desc': flow.desc,
                    'activity': flow.activity,
                    'level': {
                        'id': flow.level.id,
                        'name': flow.level.name,
                    } if flow.level else None,
                    'classes': flow.classes,
                    'students': [
                        {
                            'id': s.id,
                            'name': s.user.name,
                            'surname': s.user.surname,
                        } for s in flow.students.all()
                    ]
                }
                for flow in Flow.objects.filter(teacher=teacher).all()
            ]
        }
        return Response(info)


class SalaryYearsView(APIView):
    def get(self, request):
        teacher_id = request.query_params.get('teacher_id')
        teacher = Teacher.objects.get(pk=teacher_id)

        # Extract unique years at database level
        years = TeacherSalary.objects.filter(
            teacher=teacher
        ).annotate(
            year=ExtractYear('month_date')
        ).values_list('year', flat=True).distinct().order_by('year')
        year_list = []
        for year in years:
            info = {
                "value": year,
                "current": year == datetime.now().year
            }
            year_list.append(info)
        return Response(list(year_list))


class TeacherSalaryView(APIView):
    def get(self, request):
        teacher_id = request.query_params.get('teacher_id')
        teacher = Teacher.objects.get(pk=teacher_id)
        year = request.query_params.get('year', datetime.now().year)
        queryset = TeacherSalary.objects.filter(teacher=teacher, month_date__year=year).order_by('-month_date')
        salary_list = []
        for salary in queryset:
            salary_list.append({
                'id': salary.id,
                'date': salary.month_date.isoformat(),
                'total_salary': salary.total_salary,
                'taken_salary': salary.taken_salary,
                'remaining_salary': salary.remaining_salary,

            })
        return Response(salary_list)
