from celery import shared_task


def number_of_days_in_month(year, month):
    if month == 0:
        month = 1
    return monthrange(year, month)[1]


def weekday_from_date(day_list, month, year, week_list):
    return [days for days in day_list if day_name[date(year, month, days).weekday()] in week_list]


from calendar import monthrange, day_name
from datetime import datetime, timedelta, date

from lesson_plan.models import LessonPlan
from school_time_table.models import ClassTimeTable


def number_of_days_in_month(year, month):
    if month == 0:
        month = 1
    return monthrange(year, month)[1]


def weekday_from_date(day_list, month, year, week_list):
    return [days for days in day_list if day_name[date(year, month, days).weekday()] in week_list]


@shared_task()
def update_lesson_plan(group_id=None, flow_id=None):
    if not group_id and not flow_id:
        raise ValueError("group_id yoki flow_id berilishi kerak")

    now = datetime.now()
    start_next_week = now + timedelta(days=(7 - now.weekday()))
    end_next_week = start_next_week + timedelta(days=6)

    filters = {}

    if group_id:
        filters["group_id"] = group_id

    if flow_id:
        filters["flow_id"] = flow_id

    timetable_qs = (
        ClassTimeTable.objects
        .filter(
            date__range=[start_next_week.date(), end_next_week.date()],
            **filters
        )
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

    return True
