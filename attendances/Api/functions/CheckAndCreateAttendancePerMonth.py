from group.models import Group
from attendances.models import AttendancePerMonth, AttendancePerDay
from students.models import Student, StudentCharity
from datetime import datetime


def check_and_create_attendance_per_month(group_id, students, date):
    group = Group.objects.get(pk=group_id)
    teacher = group.teacher.first()
    today = datetime.today()
    month_date = datetime.strptime(f"{today.year}-{today.month}", "%Y-%m")
    day = datetime.strptime(f"{today.year}-{date}", "%Y-%m-%d")
    errors = []
    for student in students:
        current_month_attendance = AttendancePerMonth.objects.get_or_create(month_date=month_date, group_id=group_id,
                                                                            student_id=student['id'],
                                                                            teacher=teacher)
        try:
            attendance_per_day = AttendancePerDay.objects.get(group_id=group_id, teacher=teacher, day=day,
                                                              student_id=student['id'])
            student = Student.objects.get(pk=student['id'])
            errors.append(info={'msg': f'bu kunda {student.user.name} {student.user.surname} davomat qilingan'})
        except AttendancePerDay.DoesNotExist:
            debt_per_day = group.price / 13
            salary_per_day = group.teacher_salary / 13
            charity_data = StudentCharity.objects.get(student_id=student['id'], group_id=group_id)
            charity_per_day = charity_data.charity_sum / 13
            average = (student['homework'] + student['dictionary'] + student['active']) / 3
            AttendancePerDay.objects.create(month_date=month_date, group_id=group_id,
                                            student_id=student['id'],
                                            teacher=teacher, status=bool(student['type']),
                                            attendance_per_month=current_month_attendance, debt_per_day=debt_per_day,
                                            salary_per_day=salary_per_day, charity_per_day=charity_per_day, day=day,
                                            homework_ball=student['homework'], dictionary_ball=student['dictionary'],
                                            activeness_ball=student['active'], average=average)
            overall_salary = 0
            overall_debt = 0
            overall_charity = 0
            for attendances_pr_day in current_month_attendance.attendance_per_day.all():
                overall_salary += attendances_pr_day.salary_per_day
                overall_debt += attendances_pr_day.debt_per_day
                overall_charity += attendances_pr_day.charity_per_day
            current_month_attendance.total_debt = overall_debt
            current_month_attendance.total_salary = overall_salary
            current_month_attendance.total_charity = overall_charity
            current_month_attendance.save()
