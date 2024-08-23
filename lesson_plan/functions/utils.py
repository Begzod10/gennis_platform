import calendar
from calendar import monthrange
from datetime import datetime, date

from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from lesson_plan.models import LessonPlan, Group
from time_table.models import GroupTimeTable


def number_of_days_in_month(year, month):
    if month == 0:
        month = 1
    return monthrange(year, month)[1]


def weekday_from_date(day_list, month, year, week_list):
    filtered_days = []
    for days in day_list:
        if calendar.day_name[
            date(day=days, month=int(month), year=year).weekday()
        ] in week_list:
            filtered_days.append(days)
    return filtered_days

def update_lesson_plan( group_id):
    time_table_group = GroupTimeTable.objects.filter(group_id=group_id).order_by('id')

    week_list = [time_table.week.eng_name for time_table in time_table_group]

    current_year = datetime.now().year
    current_month = datetime.now().month

    number_days = number_of_days_in_month(current_year, current_month)

    plan_days = list(range(1, number_days + 1))
    plan_days = weekday_from_date(plan_days, current_month, current_year, week_list)

    group = get_object_or_404(Group, id=group_id)
    current_day2 = datetime.now().day + 5

    for day in plan_days:
        if current_day2 >= day:
            date_get = datetime.strptime(f"{current_year}-{current_month}-{day}", "%Y-%m-%d")
            exist = LessonPlan.objects.filter(date=date_get, group_id=group_id, teacher_id=group.teacher.id).exists()
            if not exist:
                lesson_plan = LessonPlan(group_id=group_id, teacher_id=group.teacher.id, date=date_get)
                lesson_plan.save()

    return JsonResponse({"message": "Lesson plans updated"}, status=200)
