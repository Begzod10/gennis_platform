from datetime import datetime
import pytz

from attendances.models import AttendancePerMonth

timezone = pytz.timezone('Asia/Tashkent')


def create_school_student_debts(group, students):
    today = datetime.today()
    datas = generate_months(today.year, today.month, today.year + 1, 6)
    for student in students:
        for date in datas:
            month_date = date.strftime("%Y-%m-%d")
            per_month = AttendancePerMonth.objects.get_or_create(month_date=month_date, student=student,
                                                                 total_debt=group.class_number.price, group=group,
                                                                 system=group.system)


# def generate_months(start_year, start_month, end_year, end_month):
#     if start_month == 7 or start_month == 8:
#         start_month = 9
#     current_year = start_year
#     current_month = start_month
#     dates = []
#
#     while current_year < end_year or (current_year == end_year and current_month <= end_month):
#         dates.append((current_year, current_month))
#         if current_month == 12:
#             current_month = 1
#             current_year += 1
#         else:
#             current_month += 1
#     datetime_dates = [timezone.localize(datetime(year, month, 1)) for year, month in dates]
#     sorted_datetime_dates = sorted(datetime_dates)
#
#     return sorted_datetime_dates
def generate_months(start_year, start_month, end_year, end_month):
    if start_month == 7 or start_month == 8:
        start_month = 9

    if 1 <= start_month <= 6:
        end_month = 6

    current_year = start_year
    current_month = start_month
    dates = []

    while current_year < end_year or (current_year == end_year and current_month <= end_month):
        dates.append((current_year, current_month))
        if current_month == 12:
            current_month = 1
            current_year += 1
        else:
            current_month += 1

    datetime_dates = [timezone.localize(datetime(year, month, 1)) for year, month in dates]
    sorted_datetime_dates = sorted(datetime_dates)

    return sorted_datetime_dates
