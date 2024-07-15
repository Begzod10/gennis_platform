from group.models import Group
from attendances.models import AttendancePerMonth, AttendancePerDay
from students.models import Student, StudentCharity
from datetime import datetime
from teachers.models import TeacherSalary
from ...models import GroupAttendancesPerMonth


def calculate_group_attendances(group_id, month_date):
    group = Group.objects.get(pk=group_id)
    attendances_per_month = group.attendance_per_month.filter(month_date=month_date)
    charity = 0
    salary = 0
    debt = 0
    for attendance_per_month in attendances_per_month:
        charity += attendance_per_month.total_charity
        salary += attendance_per_month.total_salary
        debt += attendance_per_month.total_debt
    try:
        current_group_attendance = GroupAttendancesPerMonth.objects.get(month_date=month_date, group_id=group_id)
        current_group_attendance.total_salary = salary
        current_group_attendance.total_debt = debt
        current_group_attendance.total_charity = charity
        current_group_attendance.save()
    except GroupAttendancesPerMonth.DoesNotExist:
        GroupAttendancesPerMonth.objects.create(total_salary=salary, total_charity=charity,
                                                total_debt=debt,
                                                group=group)
