from django.db.models import Sum, Q, Value
from teachers.models import Teacher
from observation.models import TeacherObservationDay
from django.db.models.functions import Coalesce


def get_lesson_plan_stat(teacher_id: int):
    """
    Hozircha bo'sh, keyin to'ldiramiz
    """
    return 0


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


CATEGORY_MAP = {
    "observation": get_observation_ranking,
    "lesson_plan": get_lesson_plan_stat,
}
