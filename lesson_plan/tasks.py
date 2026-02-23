from datetime import timedelta, datetime

from celery import shared_task

from lesson_plan.models import LessonPlan
from school_time_table.models import ClassTimeTable


@shared_task()
def create_lesson_plans():
    now = datetime.now()
    start_next_week = now + timedelta(days=(7 - now.weekday()))
    end_next_week = start_next_week + timedelta(days=6)

    timetable_qs = (
        ClassTimeTable.objects
        .filter(date__range=[start_next_week.date(), end_next_week.date()])
        .select_related("teacher")
    )

    for timetable in timetable_qs:
        if not timetable.teacher:
            continue

        LessonPlan.objects.get_or_create(
            group_id=timetable.group_id,
            teacher_id=timetable.teacher_id,
            date=timetable.date
        )
