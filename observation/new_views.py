from datetime import datetime
from django.db.models import Q
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from time_table.models import WeekDays
from group.models import Group
from teachers.models import Teacher
from datetime import datetime, date
from calendar import monthrange, day_name
from time_table.models import GroupTimeTable
from rest_framework.response import Response
from rest_framework.request import Request
from datetime import datetime
from Calendar.models import Years, Month, Day
from observation.models import ObservationDay, ObservationOptions, ObservationInfo, ObservationStatistics
from user.models import CustomUser
import requests


def get_json_field(request: Request, field_name: str):
    """
    Safely get a field from the JSON request body in Django REST Framework.

    Args:
        request (Request): The DRF request object.
        field_name (str): The name of the field to retrieve.

    Returns:
        Any: The value of the field if it exists, otherwise None.
    """
    return request.data.get(field_name)


def old_current_dates(group_id=0, observation=False):
    """
    :param group_id: Group's primary key
    :param observation: Boolean flag for observation mode
    :return: Old month days and current month days
    """
    current_date = datetime.now()
    current_month = current_date.month
    current_year = current_date.year
    current_day = current_date.day

    old_year = current_year
    old_month = current_month - 1

    if old_month == 0:
        old_month = 12
        old_year -= 1

    old_date = datetime.strptime(f"{old_year}-{old_month:02}", "%Y-%m")

    week_list = []
    time_table_group = GroupTimeTable.objects.filter(group_id=group_id).order_by('id')
    for time_table in time_table_group:
        week_list.append(time_table.week.eng_name)

    day_list = []
    plan_days = []
    current_month_days = number_of_days_in_month(current_year, current_month)

    for num in range(1, current_month_days + 1):
        plan_days.append(num)
        if current_day >= num:
            day_list.append(num)

    old_days = []
    old_month_days = number_of_days_in_month(old_year, old_month)

    for num in range(1, old_month_days + 1):
        old_days.append(num)

    day_list.sort()
    old_days.sort()

    if group_id != 0:
        day_list = weekday_from_date(day_list, current_month, current_year, week_list)
        old_days = weekday_from_date(old_days, old_month, old_year, week_list)

    if not observation:
        data = [
            {
                "name": current_date.strftime("%b"),  # Use current_date for name
                "value": current_date.strftime("%m"),  # Use current_date for value
                "days": day_list
            }
        ]
    else:
        data = [
            {
                "name": current_date.strftime("%b"),  # Use current_date for name
                "value": current_date.strftime("%m"),  # Use current_date for value
                "days": day_list
            },
            {
                "name": old_date.strftime("%b"),  # Use old_date for name
                "value": old_date.strftime("%m"),  # Use old_date for value
                "days": old_days
            }
        ]

    return data


def weekday_from_date(day_list, month, year, week_list):
    """
    Filter days based on week list
    :param day_list: List of days
    :param month: Month
    :param year: Year
    :param week_list: List of week day names
    :return: Filtered days
    """
    filtered_days = []
    for day in day_list:
        if day_name[date(year, month, day).weekday()] in week_list:
            filtered_days.append(day)
    return filtered_days


def number_of_days_in_month(year, month):
    """
    Get the number of days in a given month and year
    :param year: Year
    :param month: Month
    :return: Number of days
    """
    if month == 0:
        month = 1
    return monthrange(year, month)[1]


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def groups_to_observe(request, location_id=None):
    user = request.user
    if not location_id:
        location_id = user.branch.location_id
    teacher = Teacher.objects.filter(user_id=user.id).first()
    current_date = datetime.now()
    week_day_name = current_date.strftime("%A")
    get_week_day = WeekDays.objects.filter(
        name_en=week_day_name
    ).first()
    if not get_week_day:
        return JsonResponse({"error": "Week day not found."}, status=404)
    groups = Group.objects.filter(
        Q(group_time_table__week_id=get_week_day.id),
        Q(status=True),
        Q(branch__location_id=location_id),
        ~Q(teacher__id=teacher.id),
        Q(deleted=False)
    ).order_by('id')
    groups_data = [
        {
            "id": group.id,
            "name": group.name,
            "teachers": [
                {
                    "id": teacher.id,
                    "name": teacher.user.name,
                    "surname": teacher.user.surname,
                }
                for teacher in group.teacher.all()  # Iterate over the ManyToManyField
            ],
            "subject": group.subject.name,
            "level": group.level.name if group.level else None
        }
        for group in groups
    ]
    if request.method == "GET":
        return JsonResponse({
            "groups": groups_data,
            "observation_tools": old_current_dates(observation=True)
        })
    else:
        return JsonResponse({
            "groups": groups_data
        })


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def teacher_observe(request, group_id):
    user = request.user
    try:
        group = Group.objects.get(id=group_id)
    except Group.DoesNotExist:
        return Response({"error": "Group not found"}, status=404)
    if request.method == "POST":
        try:
            date = request.data.get('date')
            teacher_observation_day, created = ObservationDay.objects.get_or_create(
                teacher_id=group.teacher_id,
                day=date,
                group_id=group.id,
                defaults={"user_id": user.id}
            )
            observations = request.data.get('list', [])
            result = 0
            for item in observations:
                observation_info_id = item.get('id')
                observation_options_id = item.get('value')
                comment = item.get('comment', "")
                observation_options = ObservationOptions.objects.filter(id=observation_options_id).first()
                if observation_options:
                    result += observation_options.value
                ObservationStatistics.objects.update_or_create(
                    observation_info_id=observation_info_id,
                    observation_id=teacher_observation_day.id,
                    defaults={
                        "observation_options_id": observation_options_id,
                        "comment": comment
                    }
                )
            observation_count = ObservationInfo.objects.count()
            if observation_count > 0:
                average_result = round(result / observation_count)
                teacher_observation_day.average = average_result
                teacher_observation_day.save()

            return Response({"msg": "Teacher has been observed", "success": True})
        except Exception as e:
            return Response({"error": str(e)}, status=500)
    else:  # GET request
        observation_tools = old_current_dates(group_id=group_id, observation=True)
        return Response({"observation_tools": observation_tools})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def set_observer(request, user_id):
    try:
        user = CustomUser.objects.get(id=user_id)
        user.observer = not user.observer
        user.save()
        action = "given" if user.observer else "taken"
        response_message = f"Permission was {action}"
        success = True
        type_param = 'turon'
        classroom_server_url = f"https://classroom.gennis.uz/api/set_observer/{user.id}/?type={type_param}"
        requests.get(classroom_server_url)
        return JsonResponse({
            "msg": response_message,
            "success": success
        })
    except CustomUser.DoesNotExist:
        return JsonResponse({
            "msg": "User not found",
            "success": False
        }, status=404)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def observed_group(request, group_id, date=None):
    try:
        group = Group.objects.get(id=group_id)
        days_list = []
        month_list = []
        years_list = []
        calendar_year = datetime.now().year
        calendar_month = datetime.now().month
        if date:
            calendar_month = datetime.strptime(date, "%Y-%m")
            observation_days_all = ObservationDay.objects.filter(
                teacher_id=group.teacher_id,
                group_id=group_id,
                day__year=calendar_month.year,
                day__month=calendar_month.month
            ).order_by('id')
        else:
            observation_days_all = ObservationDay.objects.filter(
                teacher_id=group.teacher_id,
                group_id=group_id,
                day__year=calendar_year,
                day__month=calendar_month
            ).order_by('id')
        observation_days = ObservationDay.objects.filter(
            teacher_id=group.teacher_id,
            group_id=group_id,
            day__year=calendar_year,
            day__month=calendar_month
        ).order_by('id')
        for data in observation_days:
            days_list.append(data.day.strftime("%d"))
        days_list.sort()
        for plan in observation_days_all:
            month_list.append(plan.day.strftime("%m"))
            years_list.append(plan.day.strftime("%Y"))
        month_list = list(dict.fromkeys(month_list))
        years_list = list(dict.fromkeys(years_list))
        month_list.sort()
        years_list.sort()
        return JsonResponse({
            "month_list": month_list,
            "years_list": years_list,
            "month": calendar_month.strftime("%m") if month_list[-1] == calendar_month.strftime("%m") else month_list[
                -1],
            "year": calendar_month.strftime("%Y"),
            "days": days_list
        })
    except Group.DoesNotExist:
        return JsonResponse({
            "msg": "Group not found",
            "success": False
        }, status=404)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def observed_group_info(request, group_id):
    try:
        day = request.data.get('day')
        month = request.data.get('month')
        year = request.data.get('year')
        date_str = f"{year}-{month}-{day}"
        date = datetime.strptime(date_str, "%Y-%m-%d")
        observation_list = []
        observation_options = ObservationOptions.objects.all().order_by('id')
        observation_infos = ObservationInfo.objects.all().order_by('id')
        average = 0
        observer = {
            "name": "",
            "surname": ""
        }
        if date:
            teacher_observation_day = ObservationDay.objects.filter(
                group_id=group_id,
                day__year=year,
                day__month=month
            ).first()
            if teacher_observation_day:
                average = teacher_observation_day.average
                observer['name'] = teacher_observation_day.user.name
                observer['surname'] = teacher_observation_day.user.surname
            for item in observation_infos:
                teacher_observations = ObservationStatistics.objects.filter(
                    observation_id=teacher_observation_day.id,
                    observation_info_id=item.id
                ).first()
                info = {
                    "title": item.title,
                    "values": [],
                    "comment": teacher_observations.comment if teacher_observations else ""
                }
                for option in observation_options:
                    teacher_observations = ObservationStatistics.objects.filter(
                        observation_id=teacher_observation_day.id,
                        observation_options_id=option.id,
                        observation_info_id=item.id
                    ).first()

                    info["values"].append({
                        "name": option.name,
                        "value": teacher_observations.observation_option.value if teacher_observations and teacher_observations.observation_option else "",
                    })
                observation_list.append(info)
        observation_options_list = [
            {
                "id": option.id,
                "name": option.name,
                "value": option.value
            }
            for option in observation_options
        ]
        return JsonResponse({
            "info": observation_list,
            "observation_options": observation_options_list,
            "average": average,
            "observer": observer
        })
    except Exception as e:
        return JsonResponse({
            "msg": f"Error: {str(e)}",
            "success": False
        }, status=500)
