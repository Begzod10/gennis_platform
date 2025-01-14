from calendar import monthrange, day_name
from datetime import datetime, timedelta, date

from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from lesson_plan.models import LessonPlan, Group
from school_time_table.models import ClassTimeTable


def number_of_days_in_month(year, month):
    if month == 0:
        month = 1
    return monthrange(year, month)[1]


def weekday_from_date(day_list, month, year, week_list):
    return [
        days for days in day_list
        if day_name[date(year, month, days).weekday()] in week_list
    ]


def update_lesson_plan(group_id):
    time_table_group = ClassTimeTable.objects.filter(group_id=group_id).order_by('id')
    week_list = [time_table.date.strftime('%A') for time_table in time_table_group]

    current_year = datetime.now().year
    current_month = datetime.now().month
    number_days = number_of_days_in_month(current_year, current_month)
    plan_days = weekday_from_date(list(range(1, number_days + 1)), current_month, current_year, week_list)

    group = get_object_or_404(Group, id=group_id)
    current_date = datetime.now()
    future_date_limit = current_date + timedelta(days=5)

    future_days = [
        day for day in plan_days
        if current_date.date() < date(current_year, current_month, day) <= future_date_limit.date()
    ]

    valid_days = []
    for day in future_days:
        weekday = date(current_year, current_month, day).strftime('%A')
        if weekday in week_list:
            valid_days.append(day)

    for day in valid_days:
        date_get = date(current_year, current_month, day)
        teachers = group.teacher.all()
        for teacher in teachers:
            exist = LessonPlan.objects.filter(date=date_get, group_id=group_id, teacher_id=teacher.id).exists()
            if not exist:
                LessonPlan.objects.create(group_id=group_id, teacher_id=teacher.id, date=date_get)

    return JsonResponse({"message": "Lesson plans updated"}, status=200)
