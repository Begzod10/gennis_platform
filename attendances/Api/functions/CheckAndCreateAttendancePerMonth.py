from group.models import Group
from attendances.models import AttendancePerMonth, AttendancePerDay
from students.models import Student
from datetime import datetime
from teachers.models import TeacherSalary
from .CalculateGroupOverallAttendance import calculate_group_attendances


def check_and_create_attendance_per_month(group_id, students, date):
    group = Group.objects.get(pk=group_id)
    teacher = group.teacher.first()
    today = datetime.today()
    month_date = datetime.strptime(f"{today.year}-{today.month}", "%Y-%m")
    day = datetime.strptime(f"{today.year}-{date}", "%Y-%m-%d")
    errors = []
    status = False

    def update_attendance_per_month(current_month_attendance):
        overall_salary = overall_debt = overall_charity = monthly_average = 0
        for attendance in current_month_attendance.attendanceperday_set.all():
            overall_salary += attendance.salary_per_day
            overall_debt += attendance.debt_per_day
            overall_charity += attendance.charity_per_day
            monthly_average += attendance.average
        count = current_month_attendance.attendanceperday_set.count()
        current_month_attendance.total_debt = overall_debt
        current_month_attendance.total_salary = overall_salary
        current_month_attendance.total_charity = overall_charity
        current_month_attendance.ball_percentage = monthly_average / count if count else 0
        current_month_attendance.save()

    def calculate_and_create_attendance(student, current_month_attendance, charity_data=None):
        average = (student['homework'] + student['dictionary'] + student['active']) / 3
        salary_per_day = group.teacher_salary / 13
        charity_per_day = charity_data.charity_sum / 13 if charity_data else 0
        if charity_per_day == 0:
            debt_per_day = group.price / 13
        else:
            debt_per_day = (group.price / 13) - charity_per_day
        AttendancePerDay.objects.create(
            group_id=group_id,
            student_id=student['id'],
            teacher=teacher,
            status=bool(student['type']),
            attendance_per_month_id=current_month_attendance.id,
            debt_per_day=debt_per_day,
            salary_per_day=salary_per_day,
            charity_per_day=charity_per_day,
            day=day,
            homework_ball=student['homework'],
            dictionary_ball=student['dictionary'],
            activeness_ball=student['active'],
            average=average
        )

    for student in students:
        current_month_attendance, created = AttendancePerMonth.objects.get_or_create(
            month_date=month_date,
            group_id=group_id,
            student_id=student['id'],
            teacher=teacher
        )
        student_data = Student.objects.get(pk=student['id'])

        try:
            AttendancePerDay.objects.get(group_id=group_id, teacher=teacher, day=day, student_id=student['id'])
            errors.append({'msg': f'bu kunda {student_data.user.name} {student_data.user.surname} davomat qilingan'})
            return errors
        except AttendancePerDay.DoesNotExist:
            status = True
            charity_data = student_data.charity_student_id.filter(student_id=student['id'], group_id=group_id).first()
            calculate_and_create_attendance(student, current_month_attendance, charity_data)
            update_attendance_per_month(current_month_attendance)

    teacher_attendances_per_month = teacher.attendance_per_month.filter(month_date=month_date)
    salary = sum(attendance.total_salary for attendance in teacher_attendances_per_month)
    current_salary, created = TeacherSalary.objects.get_or_create(month_date=month_date,
                                                                  branch_id=group.branch_id, teacher_id=teacher.id)
    current_salary.total_salary = salary
    current_salary.save()
    calculate_group_attendances(group_id, month_date)
    return errors if not status else {'msg': 'davomat muvaffaqqiyatli kiritildi'}
