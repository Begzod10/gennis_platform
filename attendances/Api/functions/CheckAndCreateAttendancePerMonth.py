from datetime import datetime,timedelta

from attendances.models import AttendancePerMonth, AttendancePerDay
from group.models import Group
from students.models import Student
from tasks.models import TaskStatistics, TaskStudent
from teachers.models import TeacherBlackSalary
from teachers.models import TeacherSalary
from .CalculateGroupOverallAttendance import calculate_group_attendances


def check_and_create_attendance_per_month(group_id, students, date):
    group = Group.objects.get(pk=group_id)
    teacher = group.teacher.first()
    today = datetime.today()
    tomorrow = today + timedelta(days=1)
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
        student_dt = Student.objects.get(pk=student['id'])

        average = (student['homework'] + student['dictionary'] + student['active']) / 3
        salary_per_day = group.teacher_salary / 13
        if student_dt.debt_status == 2:
            black_salary, created = TeacherBlackSalary.objects.get_or_create(
                teacher_id=teacher.id,
                student_id=student['id'],
                group_id=group_id,
                month_date=month_date,
                status=False
            )
            black_salary.black_salary += salary_per_day
            black_salary.save()
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
        if created:
            if created.remaining_debt == 0:
                student.debt_status = 0
            elif student.total_payment_month > created.total_debt:
                student.debt_status = 1
                TeacherBlackSalary.objects.filter(student=student, status=False).update(status=True)
            elif student.total_payment_month < created.total_debt:
                student.debt_status = 2
                static, _ = TaskStatistics.objects.get_or_create(
                    task__name="Qarzdor uquvchilar",
                    day=tomorrow,
                    defaults={'progress_num': 100, 'percentage': 0, 'completed_num': 0, 'user': 11}
                )
                TaskStudent.objects.get_or_create(
                    task__name="Qarzdor uquvchilar",
                    task_static=static,
                    status=False,
                    students=student
                )

            student.save()
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
    teacher_black_salaries = teacher.teacher_black_salary.filter(month_date=month_date)
    overall_black_salary = 0
    for teacher_black_salary in teacher_black_salaries:
        overall_black_salary += teacher_black_salary.black_salary
    current_salary.overall_black_salary = overall_black_salary
    current_salary.total_salary = salary - current_salary.overall_black_salary
    current_salary.save()

    calculate_group_attendances(group_id, month_date)
    return errors if not status else {'msg': 'davomat muvaffaqqiyatli kiritildi'}
