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
from django.db.models import Prefetch
from django.utils import timezone
from datetime import timedelta
from django.db import transaction
from django.db.models import Avg, Count, Q, Prefetch


class TeacherGroupProfileView(APIView):
    def get(self, request):
        group_id = request.query_params.get('group_id')
        flow_status = request.query_params.get('flow')

        # Get current date info
        now = timezone.now()
        today = now.date()
        month = now.month
        year = now.year
        monday = today - timedelta(days=today.weekday())
        friday = monday + timedelta(days=4)
        is_flow = flow_status in ['true', 'True', '1']
        # Determine if it's a flow or group

        if is_flow:
            entity = Flow.objects.select_related('teacher', 'teacher__user').prefetch_related(
                Prefetch(
                    'students',
                    queryset=Student.objects.select_related('user')
                )
            ).get(pk=group_id)
            teacher = entity.teacher
            entity_name = entity.name
            filter_field = 'flow_id'
        else:
            entity = Group.objects.select_related(
                'class_number', 'color'
            ).prefetch_related(
                Prefetch(
                    'students',
                    queryset=Student.objects.select_related('user')
                ),
                Prefetch(
                    'teacher',
                    queryset=Teacher.objects.select_related('user')
                )
            ).get(pk=group_id)
            teacher = entity.teacher.first()
            entity_name = f"{entity.class_number.number}-{entity.color.name}"
            filter_field = 'group_id'

        # Get schedules for current week
        schedule_filter = {
            filter_field: group_id,
            'date__gte': monday,
            'date__lte': friday
        }
        class_schedule = ClassTimeTable.objects.filter(
            **schedule_filter
        ).select_related(
            'week', 'room', 'hours', 'subject'
        ).order_by('date', 'hours__start_time')

        # Get next lesson
        next_lesson_filter = {
            filter_field: group_id,
            'date__gt': today
        }
        next_lesson = ClassTimeTable.objects.filter(
            **next_lesson_filter
        ).select_related('hours').order_by('date', 'hours__start_time').first()

        # Build base info
        info = {
            "group_name": entity_name,
            "group_id": entity.id,
            "students_count": entity.students.count(),
            "next_lesson": next_lesson.date.strftime('%Y-%m-%d') if next_lesson else None,
            "start_time": next_lesson.hours.start_time.strftime('%H:%M') if next_lesson else None,
            "students": [],
            "schedule": []
        }

        # Get all student scores in bulk
        score_filter = {
            'teacher': teacher,
            'day__month': month,
            'day__year': year
        }
        if is_flow:
            score_filter['flow'] = entity
        else:
            score_filter['group'] = entity

        # Aggregate attendance and scores per student
        student_scores = StudentScoreByTeacher.objects.filter(
            **score_filter
        ).values('student_id').annotate(
            avg_score=Avg('average'),
            total_count=Count('id'),
            present_count=Count('id', filter=Q(status=True))
        )

        # Convert to dictionary for O(1) lookup
        scores_dict = {
            item['student_id']: {
                'average': round(item['avg_score']) if item['avg_score'] else 0,
                'present_percent': round(item['present_count'] / item['total_count'] * 100, 2) if item[
                    'total_count'] else 0
            }
            for item in student_scores
        }

        # Build student list
        for student in entity.students.all():
            student_data = scores_dict.get(student.id, {'average': 0, 'present_percent': 0})
            today_score = StudentScoreByTeacher.objects.filter(
                student=student,
                teacher=teacher,
                group_id=group_id if not is_flow else None,
                flow_id=group_id if is_flow else None,
                day__day=today.day
            ).exists()
            info['students'].append({
                'id': student.id,
                'name': student.user.name,
                'surname': student.user.surname,
                'average': student_data['average'],
                'present_percent': student_data['present_percent'],
                'marked': today_score
            })

        # Build schedule list
        info['schedule'] = [
            {
                'date': schedule.date,
                'week_day': schedule.week.name_en if schedule.week else None,
                'room': schedule.room.name if schedule.room else None,
                'time': f"{schedule.hours.start_time} - {schedule.hours.end_time}",
                'subject': schedule.subject.name if schedule.subject else None,
            }
            for schedule in class_schedule
        ]

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


class TeacherClassesView(APIView):
    def get(self, request):
        today = timezone.now().date()
        monday = today - timedelta(days=today.weekday())
        friday = monday + timedelta(days=4)
        teacher_id = request.query_params.get('teacher_id')

        # Single optimized query with select_related
        base_query = ClassTimeTable.objects.filter(
            teacher_id=teacher_id,
            date__gte=monday,
            date__lte=friday
        ).select_related(
            'week', 'room', 'hours', 'subject', 'flow', 'group', 'group__class_number', 'group__color'
        ).order_by('date', 'hours__start_time')

        # Get unique flow_ids and group_ids
        flow_ids = base_query.filter(
            flow_id__isnull=False
        ).values_list('flow_id', flat=True).distinct()

        group_ids = base_query.filter(
            group_id__isnull=False
        ).values_list('group_id', flat=True).distinct()

        # Prefetch flows and groups with their schedules
        flows = Flow.objects.filter(id__in=flow_ids).prefetch_related(
            Prefetch(
                'classtimetable_set',
                queryset=base_query.filter(flow_id__isnull=False),
                to_attr='current_week_schedules'
            )
        )

        groups = Group.objects.filter(id__in=group_ids).select_related(
            'class_number', 'color'
        ).prefetch_related(
            Prefetch(
                'classtimetable_set',
                queryset=base_query.filter(group_id__isnull=False),
                to_attr='current_week_schedules'
            )
        )

        # Get next lessons in one query for flows
        next_flow_lessons = {
            lesson.flow_id: lesson
            for lesson in ClassTimeTable.objects.filter(
                flow_id__in=flow_ids,
                date__gt=today
            ).select_related('hours').order_by('flow_id', 'date', 'hours__start_time').distinct('flow_id')
        }

        # Get next lessons in one query for groups
        next_group_lessons = {
            lesson.group_id: lesson
            for lesson in ClassTimeTable.objects.filter(
                group_id__in=group_ids,
                date__gt=today
            ).select_related('hours').order_by('group_id', 'date', 'hours__start_time').distinct('group_id')
        }

        classes = []

        # Process flows
        for flow in flows:
            next_lesson = next_flow_lessons.get(flow.id)

            classes.append({
                'id': flow.id,
                'name': flow.name,
                'flow': True,
                'schedules': [
                    {
                        'date': schedule.date,
                        'week_day': schedule.week.name_en if schedule.week else None,
                        'room': schedule.room.name if schedule.room else None,
                        'time': f"{schedule.hours.start_time} - {schedule.hours.end_time}",
                        'subject': schedule.subject.name if schedule.subject else None,
                    }
                    for schedule in flow.current_week_schedules
                ],
                'next_lesson': {
                    'date': next_lesson.date.strftime('%Y-%m-%d') if next_lesson else None,
                    'time': str(next_lesson.hours.start_time) if next_lesson else None,
                }
            })

        # Process groups
        for group in groups:
            next_lesson = next_group_lessons.get(group.id)

            classes.append({
                'id': group.id,
                'name': f"{group.class_number.number}-{group.color.name}",
                'flow': False,
                'schedules': [
                    {
                        'date': schedule.date,
                        'week_day': schedule.week.name_en if schedule.week else None,
                        'room': schedule.room.name if schedule.room else None,
                        'time': f"{schedule.hours.start_time} - {schedule.hours.end_time}",
                        'subject': schedule.subject.name if schedule.subject else None,
                    }
                    for schedule in group.current_week_schedules
                ],
                'next_lesson': {
                    'date': next_lesson.date.strftime('%Y-%m-%d') if next_lesson else None,
                    'time': str(next_lesson.hours.start_time) if next_lesson else None,
                }
            })

        return Response({'classes': classes})


class StudentScoreView(APIView):
    def post(self, request):
        day = request.data.get('day')
        student_list = request.data.get('student_list')
        flow_status = request.query_params.get('flow')
        group_id = request.query_params.get('group_id')

        is_flow = flow_status in ['true', 'True', '1']

        # Get the appropriate object once
        parent_obj = Flow.objects.get(id=group_id) if is_flow else Group.objects.get(id=group_id)
        filter_key = 'flow' if is_flow else 'group'
        if is_flow:
            teacher = parent_obj.teacher  # ForeignKey - returns Teacher object directly
        else:
            teacher = parent_obj.teacher.first()
            # Fetch all existing scores in one query
        existing_scores = StudentScoreByTeacher.objects.filter(
            **{filter_key: parent_obj},
            student_id__in=[s['id'] for s in student_list],
            day=day
        )

        # Create a lookup dictionary for O(1) access
        score_lookup = {score.student_id: score for score in existing_scores}

        scores_to_update = []
        scores_to_create = []

        for student in student_list:
            student_id = student['id']
            status = student.get('status')

            # Calculate scores
            if status:
                homework = student.get('homework', 0)
                activeness = student.get('activeness', 0)
                average = round((homework + activeness) / 2)
            else:
                homework = activeness = average = 0

            # Check if score exists
            if student_id in score_lookup:
                student_score = score_lookup[student_id]
                student_score.homework = homework
                student_score.activeness = activeness
                student_score.average = average
                student_score.status = status
                scores_to_update.append(student_score)
            else:
                scores_to_create.append(StudentScoreByTeacher(
                    **{filter_key: parent_obj},
                    student_id=student_id,
                    day=day,
                    teacher_id=teacher.id,
                    homework=homework,
                    activeness=activeness,
                    average=average,
                    status=status
                ))

        # Perform bulk operations in a transaction
        with transaction.atomic():
            if scores_to_update:
                StudentScoreByTeacher.objects.bulk_update(
                    scores_to_update,
                    ['homework', 'activeness', 'average', 'status']
                )
            if scores_to_create:
                StudentScoreByTeacher.objects.bulk_create(scores_to_create)

        return Response({'status': 'success'})
