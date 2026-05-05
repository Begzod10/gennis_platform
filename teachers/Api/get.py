from django.utils import timezone
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from permissions.response import QueryParamFilterMixin
from teachers.models import TeacherAttendance, Teacher, TeacherSalaryType
from teachers.serializers import TeacherAttendanceListSerializers, TeacherSerializerRead, \
    TeacherSalaryTypeSerializerRead
from teachers.serializer.lists import ActiveListTeacherSerializerTime
from teachers.services.teacher_rating import CATEGORY_MAP


class TeacherAttendanceListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = TeacherAttendance.objects.all()
    serializer_class = TeacherAttendanceListSerializers

    def get(self, request, *args, **kwargs):
        queryset = TeacherAttendance.objects.all()

        serializer = TeacherAttendanceListSerializers(queryset, many=True)
        return Response(serializer.data)


class TeacherAttendanceRetrieveView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TeacherAttendanceListSerializers

    def get_queryset(self):
        teacher_id = self.kwargs['pk']

        today = timezone.now().date()

        year = self.request.query_params.get('year', today.year)
        month = self.request.query_params.get('month', today.month)
        day = self.request.query_params.get('day')

        qs = TeacherAttendance.objects.filter(
            teacher_id=teacher_id,
            day__year=year,
            day__month=month
        )

        if day:
            qs = qs.filter(day__day=day)

        return qs


class TeachersForBranches(generics.ListAPIView):
    permission_classes = [IsAuthenticated]

    serializer_class = TeacherSerializerRead

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        return Teacher.objects.filter(branches__in=[pk])


class TeachersForSubject(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TeacherSerializerRead

    def get_queryset(self):
        branch_id = self.request.query_params.get('branch')
        subject_id = self.request.query_params.get('subject')

        return Teacher.objects.filter(branches__in=[branch_id], subject__in=[subject_id])


class TeachersForSubjectForTimeTable(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ActiveListTeacherSerializerTime

    def get_queryset(self):
        branch_id = self.request.query_params.get('branch')
        subject_id = self.request.query_params.get('subject')

        return Teacher.objects.filter(branches__in=[branch_id], subject__in=[subject_id]).all()


class SalaryType(QueryParamFilterMixin, generics.ListCreateAPIView):
    filter_mappings = {
        'branch': 'branch_id',
    }
    serializer_class = TeacherSalaryTypeSerializerRead
    queryset = TeacherSalaryType.objects.all()


class TeacherRatingAPIView(APIView):

    def get(self, request):
        branch_id = request.query_params.get('branch')
        category = request.query_params.get('category')
        year = request.query_params.get('year')
        month = request.query_params.get('month')
        year = int(year) if year else None
        month = int(month) if month else None

        if category not in CATEGORY_MAP:
            return Response({"detail": "Invalid category"}, status=400)

        data = CATEGORY_MAP[category](branch_id, year, month)

        return Response(data)


class TeacherStatAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get_date_range(self, filter_type):
        today = date.today()

        if filter_type == 'last_week':
            return today - timedelta(days=7), today
        elif filter_type == 'last_month':
            return today - timedelta(days=30), today
        elif filter_type == 'this_month':
            return today.replace(day=1), today
        elif filter_type == 'this_week':
            return today - timedelta(days=today.weekday()), today
        else:
            return today - timedelta(days=30), today

    def get(self, request, teacher_id=None):
        filter_type = request.query_params.get('filter', 'last_month')
        date_from_str = request.query_params.get('date_from')
        date_to_str = request.query_params.get('date_to')
        branch_id = request.query_params.get('branch')  # 👈 yangi param

        date_from, date_to = self.get_date_range(filter_type)

        if filter_type == 'custom' and date_from_str and date_to_str:
            from datetime import datetime
            date_from = datetime.strptime(date_from_str, '%Y-%m-%d').date()
            date_to = datetime.strptime(date_to_str, '%Y-%m-%d').date()

        # Teacher query
        teachers_qs = Teacher.objects.filter(deleted=False).select_related('user', 'user__branch')

        if teacher_id:
            teachers_qs = teachers_qs.filter(id=teacher_id)

        # Branch filter — teacher.user.branch orqali
        if branch_id:
            teachers_qs = teachers_qs.filter(user__branch_id=branch_id)

        result = []

        for teacher in teachers_qs:
            user = teacher.user

            # ObservationDay
            observations = ObservationDay.objects.filter(
                teacher=teacher,
                deleted=False,
                day__range=(date_from, date_to)
            )
            obs_count = observations.count()
            obs_avg = observations.aggregate(avg=Avg('average'))['avg'] or 0

            # LessonPlan
            lesson_plans = LessonPlan.objects.filter(
                teacher=teacher,
                date__range=(date_from, date_to)
            )
            lp_count = lesson_plans.count()
            lp_avg_ball = lesson_plans.aggregate(avg=Avg('ball'))['avg'] or 0

            # Mission
            missions = Mission.objects.filter(
                executor=user,
                start_date__range=(date_from, date_to)
            )
            mission_total = missions.count()
            mission_completed = missions.filter(status__in=['completed', 'approved']).count()
            mission_avg_score = missions.aggregate(avg=Avg('final_sc'))['avg'] or 0
            mission_delay_avg = missions.aggregate(avg=Avg('delay_days'))['avg'] or 0

            result.append({
                'teacher_id': teacher.id,
                'teacher_name': f"{user.name} {user.surname}",
                'branch': {
                    'id': user.branch.id if user.branch else None,
                    'name': str(user.branch) if user.branch else None,
                },
                'period': f"{date_from} / {date_to}",
                'filter_type': filter_type,
                'observation_count': obs_count,
                'observation_avg': round(obs_avg, 2),
                'lesson_plan_count': lp_count,
                'lesson_plan_avg_ball': round(lp_avg_ball, 2),
                'mission_total': mission_total,
                'mission_completed': mission_completed,
                'mission_avg_score': round(mission_avg_score, 2),
                'mission_delay_days': round(mission_delay_avg, 2),
            })

        return Response({
            'date_from': str(date_from),
            'date_to': str(date_to),
            'filter': filter_type,
            'branch_id': branch_id,
            'count': len(result),
            'results': result
        })
