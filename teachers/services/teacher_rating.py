from django.db.models import Count, Q, F, Case, When, Value, FloatField, ExpressionWrapper, Sum, IntegerField, Avg
from teachers.models import Teacher
from observation.models import TeacherObservationDay
from django.db.models.functions import Coalesce
from datetime import date
import calendar


def get_satisfaction_ranking(branch_id=None, year=None, month=None):
    filters = Q()

    if branch_id:
        filters &= Q(user__branch_id=int(branch_id))

    today = date.today()

    if year and month:
        year = int(year)
        month = int(month)

        if year == today.year and month == today.month:
            filters &= Q(
                satisfactionsurvey__datetime__year=year,
                satisfactionsurvey__datetime__month=month,
                satisfactionsurvey__datetime__day__lte=today.day
            )
        else:
            filters &= Q(
                satisfactionsurvey__datetime__year=year,
                satisfactionsurvey__datetime__month=month
            )

    teachers = (
        Teacher.objects
        .filter(filters)
        .select_related("user")
        .annotate(
            ball=Avg("satisfactionsurvey__score"),
            count=Count("satisfactionsurvey")
        )
        .order_by("-ball")
    )

    return [
        {
            "id": t.id,
            "name": t.user.name,
            "surname": t.user.surname,
            "ball": int(t.ball) if t.ball else 0,
            "count": t.count or 0,
        }
        for t in teachers
    ]


def get_student_results_ranking(branch_id=None, year=None, month=None):
    today = date.today()

    # year/month kelmasa current month ishlaydi
    year = int(year) if year else today.year
    month = int(month) if month else today.month

    filters = Q(exam_results__datetime__year=year) & Q(
        exam_results__datetime__month=month
    )

    teachers = (
        Teacher.objects
        .select_related("user")
        .annotate(
            avg_score=Coalesce(
                Avg("exam_results__score", filter=filters),
                Value(0),
                output_field=FloatField()
            ),
            total_exams=Count(
                "exam_results",
                filter=filters
            ),
        )
    )

    if branch_id:
        teachers = teachers.filter(user__branch_id=int(branch_id))

    teachers = teachers.order_by("-avg_score")

    return [
        {
            "id": t.id,
            "name": t.user.name,
            "surname": t.user.surname,
            "percent": round(t.avg_score or 0, 1),
            "total": t.total_exams,
            "done": t.total_exams
        }
        for t in teachers
    ]


def get_lesson_plan_ranking(branch_id, year=None, month=None):
    today = date.today()

    date_filter = Q()
    year = int(year) if year else today.year
    month = int(month) if month else today.month

    if year == today.year and month == today.month:
        # hozirgi oy → bugungacha
        date_filter &= Q(lessonplan__date__year=year)
        date_filter &= Q(lessonplan__date__month=month)
        date_filter &= Q(lessonplan__date__lte=today)
    else:
        # oldingi oy → to‘liq oy
        date_filter &= Q(lessonplan__date__year=year)
        date_filter &= Q(lessonplan__date__month=month)

    teachers = (
        Teacher.objects
        .filter(
            user__branch_id=branch_id,
            deleted=False
        )
        .select_related('user')
        .annotate(
            total_plans=Count(
                'lessonplan',
                filter=date_filter,
                distinct=True
            ),
            done_plans=Count(
                'lessonplan',
                filter=date_filter & ~Q(lessonplan__objective__isnull=True),
                distinct=True
            )
        )
        .annotate(
            percent=Case(
                When(total_plans=0, then=Value(0)),
                default=F('done_plans') * 100 / F('total_plans'),
                output_field=IntegerField()
            )
        )
        .order_by('-percent')
    )

    return [
        {
            "id": t.id,
            "name": t.user.name,
            "surname": t.user.surname,
            "percent": t.percent,
            "total": t.total_plans,
            "done": t.done_plans
        }
        for t in teachers
    ]


def get_observation_ranking(branch_id, year=None, month=None):
    filters = Q()

    if year:
        filters &= Q(teacherobservationday__date__year=int(year))

    if month:
        filters &= Q(teacherobservationday__date__month=int(month))

    teachers = (
        Teacher.objects
        .filter(
            user__branch_id=int(branch_id),
            deleted=False
        )
        .select_related('user')
        .annotate(
            ball=Coalesce(
                Sum(
                    'teacherobservationday__average',
                    filter=filters
                ),
                Value(0)
            )
        )
        .order_by('-ball')
    )

    return [
        {
            "id": t.id,
            "name": t.user.name,
            "surname": t.user.surname,
            "ball": t.ball
        }
        for t in teachers
    ]


def get_contribution_ranking(branch_id=None, year=None, month=None):
    filters = Q()

    # branch filter
    if branch_id:
        filters &= Q(user__branch_id=int(branch_id))

    today = date.today()
    year = int(year) if year else today.year
    month = int(month) if month else today.month

    # date filter
    if year and month:
        year = int(year)
        month = int(month)

        if year == today.year and month == today.month:
            filters &= Q(
                contributions__datetime__year=year,
                contributions__datetime__month=month,
                contributions__datetime__day__lte=today.day
            )
        else:
            filters &= Q(
                contributions__datetime__year=year,
                contributions__datetime__month=month
            )

    teachers = (
        Teacher.objects
        .filter(filters)
        .select_related("user")
        .annotate(
            ball=Avg("contributions__score"),
            count=Count("contributions")
        )
        .order_by("-ball")
    )

    return [
        {
            "id": t.id,
            "name": t.user.name,
            "surname": t.user.surname,
            "ball": round(t.ball, 2) if t.ball else 0,
            "count": t.count or 0,
        }
        for t in teachers
    ]


CATEGORY_MAP = {
    "observation": get_observation_ranking,
    "lesson_plan": get_lesson_plan_ranking,
    "student_results": get_student_results_ranking,
    "satisfaction": get_satisfaction_ranking,
    "contribution": get_contribution_ranking,
}
