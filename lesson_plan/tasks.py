from datetime import timedelta, datetime

from celery import shared_task

from lesson_plan.models import LessonPlan
from school_time_table.models import ClassTimeTable


@shared_task
def create_lesson_plans():
    now = datetime.now()
    start_date = now.date()
    end_date = start_date + timedelta(days=8)

    timetable_qs = (
        ClassTimeTable.objects
        .filter(date__range=[start_date, end_date])
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