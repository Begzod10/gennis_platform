from django.utils import timezone
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from .models import Survey, SurveySubmission, SurveyAnswer
from .serializers import (
    SurveyAdminCreateSerializer,
    SurveyAdminUpdateSerializer,
    SurveyAdminListSerializer,
    SurveyAdminDetailSerializer,
    SurveyMobileListSerializer,
    SurveyMobileDetailSerializer,
    SurveySubmitSerializer,
    SurveySubmissionListSerializer,
    SurveySubmissionDetailSerializer,
)



def get_role_info(user):

    if hasattr(user, 'student_user') and user.student_user.exists():
        return {'role': 'student', 'student': user.student_user.first()}
    if hasattr(user, 'teacher_user') and user.teacher_user.exists():
        return {'role': 'teacher', 'teacher': user.teacher_user.first()}
    if hasattr(user, 'parent_set') and user.parent_set.exists():
        return {'role': 'parent', 'parent': user.parent_set.first()}
    return {'role': None}


def get_available_surveys(user):

    role_info = get_role_info(user)
    role = role_info.get('role')
    now = timezone.now()

    if role:
        role_filter = ['all', role]
    else:
        role_filter = ['all']

    qs = Survey.objects.filter(
        is_active=True,
        deadline__gt=now,
        target_role__in=role_filter,
    )

    user_branch = user.branch
    if user_branch:
        qs = qs.filter(
            models_Q(branch__isnull=True) | models_Q(branch=user_branch)
        )
    else:
        qs = qs.filter(branch__isnull=True)

    return qs


from django.db.models import Q as models_Q


def get_surveys_excluding_completed(user):

    qs = get_available_surveys(user)


    completed_ids = SurveySubmission.objects.filter(
        respondent=user,
        target_teacher__isnull=True
    ).values_list('survey_id', flat=True)

    qs = qs.exclude(id__in=completed_ids)
    return qs



class AdminSurveyListCreateView(generics.ListCreateAPIView):

    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return SurveyAdminCreateSerializer
        return SurveyAdminListSerializer

    def get_queryset(self):
        qs = Survey.objects.all()
        target = self.request.query_params.get('target_role')
        branch = self.request.query_params.get('branch')
        if target:
            qs = qs.filter(target_role=target)
        if branch:
            qs = qs.filter(branch_id=branch)
        return qs


class AdminSurveyDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Survey.objects.all()

    def get_serializer_class(self):
        if self.request.method in ('PUT', 'PATCH'):
            return SurveyAdminUpdateSerializer
        return SurveyAdminDetailSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {"detail": "success deleted"},
            status=status.HTTP_200_OK
        )

class AdminSurveySubmissionsView(generics.ListAPIView):

    permission_classes = [IsAuthenticated]
    serializer_class = SurveySubmissionListSerializer

    def get_queryset(self):
        qs = SurveySubmission.objects.filter(
            survey_id=self.kwargs['pk']
        ).select_related('respondent', 'target_teacher__user', 'branch').order_by('-submitted_at')

        role = self.request.query_params.get('role')
        branch = self.request.query_params.get('branch')
        if role:
            qs = qs.filter(respondent_role=role)
        if branch:
            qs = qs.filter(branch_id=branch)
        return qs


class AdminSubmissionDetailView(generics.RetrieveAPIView):

    permission_classes = [IsAuthenticated]
    queryset = SurveySubmission.objects.all()
    serializer_class = SurveySubmissionDetailSerializer


class AdminSurveyStatisticsView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            survey = Survey.objects.get(pk=pk)
        except Survey.DoesNotExist:
            return Response({'detail': 'Topilmadi.'}, status=404)

        teacher_id = request.query_params.get('teacher_id')
        teacher = None
        if teacher_id:
            from teachers.models import Teacher
            try:
                teacher = Teacher.objects.get(pk=teacher_id)
            except Teacher.DoesNotExist:
                return Response({'detail': "O'qituvchi topilmadi."}, status=404)

        return Response(_build_statistics_with_ai(survey, teacher_filter=teacher))


class MobileSurveyListView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        role_info = get_role_info(user)
        role = role_info.get('role')

        qs = get_available_surveys(user)

        if role == 'teacher':

            completed_general = SurveySubmission.objects.filter(
                respondent=user,
                target_teacher__isnull=True
            ).values_list('survey_id', flat=True)
            qs = qs.exclude(id__in=completed_general)
        else:
            qs = get_surveys_excluding_completed(user)

        serializer = SurveyMobileListSerializer(qs, many=True)
        return Response({'success': True, 'data': serializer.data})


class MobileSurveyDetailView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        user = request.user
        try:
            survey = get_available_surveys(user).get(pk=pk)
        except Survey.DoesNotExist:
            return Response({'detail': 'Topilmadi yoki ruxsat yo\'q.'}, status=404)

        serializer = SurveyMobileDetailSerializer(survey)
        return Response({'success': True, 'data': serializer.data})



class MobileTeacherListForSurveyView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        user = request.user

        try:
            survey = get_available_surveys(user).get(pk=pk)
        except Survey.DoesNotExist:
            return Response({'detail': 'Topilmadi yoki ruxsat yo\'q.'}, status=404)

        role_info = get_role_info(user)
        role = role_info.get('role')

        from teachers.models import Teacher
        teacher_ids = set()

        if role == 'student':
            student = role_info.get('student')
            if student:
                from group.models import Group
                groups = Group.objects.filter(students=student, deleted=False)
                for g in groups:
                    for t in g.teacher.filter(deleted=False):
                        teacher_ids.add(t.id)

        elif role == 'parent':
            parent = role_info.get('parent')
            if parent:
                from group.models import Group
                children = parent.children.all()
                groups = Group.objects.filter(students__in=children, deleted=False).distinct()
                for g in groups:
                    for t in g.teacher.filter(deleted=False):
                        teacher_ids.add(t.id)

        elif role == 'teacher':
            current_teacher = role_info.get('teacher')
            if current_teacher and user.branch:
                teachers = Teacher.objects.filter(
                    branches=user.branch,
                    deleted=False
                ).exclude(id=current_teacher.id)
                teacher_ids = set(teachers.values_list('id', flat=True))

        teachers = Teacher.objects.filter(
            id__in=teacher_ids
        ).select_related('user')

        result = []
        for t in teachers:
            is_completed = SurveySubmission.objects.filter(
                survey=survey,
                respondent=user,
                target_teacher=t
            ).exists()

            result.append({
                'teacher_id': t.id,
                'teacher_name': f"{t.user.name} {t.user.surname}".strip(),
                'is_completed': is_completed,
            })

        return Response({'success': True, 'data': result})




class MobileSurveySubmitView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        user = request.user

        try:
            survey = get_available_surveys(user).get(pk=pk)
        except Survey.DoesNotExist:
            return Response(
                {'success': False, 'detail': 'So\'rovnoma topilmadi yoki muddati tugagan.'},
                status=404
            )

        role_info = get_role_info(user)

        # Teacher o'zini to'ldira olmaydi (target_teacher = o'zi bo'lsa)
        teacher_id = request.data.get('teacher_id')
        if role_info.get('role') == 'teacher' and teacher_id:
            current_teacher = role_info.get('teacher')
            if current_teacher and current_teacher.id == int(teacher_id):
                return Response(
                    {'success': False, 'detail': 'O\'zingiz haqingizda so\'rovnoma to\'ldira olmaysiz.'},
                    status=400
                )

        serializer = SurveySubmitSerializer(
            data=request.data,
            context={'request': request, 'survey': survey, 'role_info': role_info}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                {'success': True, 'message': 'So\'rovnoma muvaffaqiyatli yuborildi.'},
                status=201
            )
        return Response({'success': False, 'errors': serializer.errors}, status=400)




class MobileMyStatisticsView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        teacher = user.teacher_user.first() if hasattr(user, 'teacher_user') else None
        if not teacher:
            return Response({'detail': 'Faqat o\'qituvchilar uchun.'}, status=403)

        survey_id = request.query_params.get('survey_id')
        submissions = SurveySubmission.objects.filter(target_teacher=teacher)

        surveys_qs = Survey.objects.filter(
            submissions__target_teacher=teacher
        ).distinct()

        if survey_id:
            surveys_qs = surveys_qs.filter(id=survey_id)

        total_responses = submissions.count()
        overall_score = _compute_overall_score(submissions)

        surveys_data = []
        for survey in surveys_qs:
            s_submissions = submissions.filter(survey=survey)
            stats = _build_statistics_with_ai(survey, teacher_filter=teacher)
            surveys_data.append({
                'survey_id': survey.id,
                'survey_title': survey.title,
                'responses_count': s_submissions.count(),
                'questions': stats['questions'],
            })

        return Response({
            'total_responses': total_responses,
            'overall_score': overall_score,
            'surveys': surveys_data,
        })




def _compute_overall_score(submissions):
    answers = SurveyAnswer.objects.filter(
        submission__in=submissions,
        question__type='star'
    )
    values = []
    for a in answers:
        try:
            values.append(float(a.value))
        except (ValueError, TypeError):
            pass
    if not values:
        return None
    return round(sum(values) / len(values), 2)


def _build_statistics(survey, teacher_filter=None):
    submissions = SurveySubmission.objects.filter(survey=survey)
    if teacher_filter:
        submissions = submissions.filter(target_teacher=teacher_filter)

    answers_qs = SurveyAnswer.objects.filter(submission__in=submissions)
    questions_data = []

    for q in survey.questions.prefetch_related('options').order_by('order'):
        q_answers = answers_qs.filter(question=q)
        q_stat = {'question_id': q.id, 'text': q.text, 'type': q.type, 'stats': {}}

        if q.type == 'yes_no':
            yes = q_answers.filter(value='yes').count()
            no = q_answers.filter(value='no').count()
            total = yes + no
            q_stat['stats'] = {
                'yes_count': yes,
                'no_count': no,
                'yes_percentage': round(yes / total * 100, 1) if total else 0,
            }

        elif q.type == 'star':
            values = []
            dist = {str(i): 0 for i in range(1, 6)}
            for a in q_answers:
                try:
                    v = int(a.value)
                    if 1 <= v <= 5:
                        values.append(v)
                        dist[str(v)] += 1
                except (ValueError, TypeError):
                    pass
            q_stat['stats'] = {
                'average': round(sum(values) / len(values), 2) if values else 0,
                'distribution': dist,
            }

        elif q.type == 'test':
            total = q_answers.count()
            options_stat = []
            for opt in q.options.all():
                cnt = q_answers.filter(value=str(opt.id)).count()
                options_stat.append({
                    'id': opt.id,
                    'text': opt.text,
                    'count': cnt,
                    'percentage': round(cnt / total * 100, 1) if total else 0,
                })
            q_stat['stats'] = {'options': options_stat}

        elif q.type == 'short_answer':
            q_stat['stats'] = {
                'total_answers': q_answers.exclude(value='').count(),
                'ai_summary': None,
            }

        questions_data.append(q_stat)

    return {
        'survey_id': survey.id,
        'survey_title': survey.title,
        'total_responses': submissions.count(),
        'questions': questions_data,
    }


def _build_statistics_with_ai(survey, teacher_filter=None):

    from .utils import analyze_short_answers

    submissions = SurveySubmission.objects.filter(survey=survey)
    if teacher_filter:
        submissions = submissions.filter(target_teacher=teacher_filter)

    answers_qs = SurveyAnswer.objects.filter(submission__in=submissions)
    questions_data = []

    for q in survey.questions.prefetch_related('options').order_by('order'):
        q_answers = answers_qs.filter(question=q)
        q_stat = {'question_id': q.id, 'text': q.text, 'type': q.type, 'stats': {}}

        if q.type == 'yes_no':
            yes = q_answers.filter(value='yes').count()
            no = q_answers.filter(value='no').count()
            total = yes + no
            q_stat['stats'] = {
                'yes_count': yes,
                'no_count': no,
                'yes_percentage': round(yes / total * 100, 1) if total else 0,
            }

        elif q.type == 'star':
            values = []
            dist = {str(i): 0 for i in range(1, 6)}
            for a in q_answers:
                try:
                    v = int(a.value)
                    if 1 <= v <= 5:
                        values.append(v)
                        dist[str(v)] += 1
                except (ValueError, TypeError):
                    pass
            q_stat['stats'] = {
                'average': round(sum(values) / len(values), 2) if values else 0,
                'distribution': dist,
            }

        elif q.type == 'test':
            total = q_answers.count()
            options_stat = []
            for opt in q.options.all():
                cnt = q_answers.filter(value=str(opt.id)).count()
                options_stat.append({
                    'id': opt.id,
                    'text': opt.text,
                    'count': cnt,
                    'percentage': round(cnt / total * 100, 1) if total else 0,
                })
            q_stat['stats'] = {'options': options_stat}

        elif q.type == 'short_answer':
            text_answers = list(
                q_answers.exclude(value='').values_list('value', flat=True)
            )
            total_answers = len(text_answers)

            if total_answers > 0:
                ai_result = analyze_short_answers(q.text, text_answers)
            else:
                ai_result = {'ai_summary': None, 'sentiment': {'positive': 0, 'neutral': 0, 'negative': 0}}

            q_stat['stats'] = {
                'total_answers': total_answers,
                'ai_summary': ai_result['ai_summary'],
                'sentiment': ai_result['sentiment'],
            }

        questions_data.append(q_stat)

    return {
        'survey_id': survey.id,
        'survey_title': survey.title,
        'total_responses': submissions.count(),
        'questions': questions_data,
    }