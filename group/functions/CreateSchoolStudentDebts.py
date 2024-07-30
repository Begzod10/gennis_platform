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
            print(month_date)
            per_month = AttendancePerMonth.objects.create(month_date=month_date, student=student,
                                                          total_debt=group.price, group=group,
                                                          teacher=group.teacher.first(), system=group.system)
            print(per_month)


def generate_months(start_year, start_month, end_year, end_month):
    if start_month == 7 or start_month == 8:
        start_month = 9
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
