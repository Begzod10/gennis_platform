from Calendar.models import Day
from datetime import datetime

from Calendar.models import Day
from flows.models import Flow
from school_time_table.models import ClassTimeTable
from teachers.models import TeacherSalary, Teacher

from datetime import date, timedelta


def working_days_in_month(year, month):
    first_day = date(year, month, 1)
    last_day = date(year, month + 1, 1) - timedelta(days=1) if month < 12 else date(year, 12, 31)

    workdays = sum(1 for day in range((last_day - first_day).days + 1)
                   if (first_day + timedelta(days=day)).weekday() < 5)  # 0-4 are weekdays (Mon-Fri)

    return workdays


# Example usage:


def calculate_teacher_salary(teacher):
    today = datetime.now()
    teacher_get = Teacher.objects.get(user=teacher.user)
    if teacher_get:
        old_month_date = datetime(today.year, today.month - 1, 1)
        old_exist_salary = TeacherSalary.objects.filter(teacher=teacher, month_date=old_month_date).exists()
        if not old_exist_salary:
            if teacher.teacher_salary_type is not None:
                salary, _ = TeacherSalary.objects.get_or_create(
                    teacher=teacher,
                    month_date=old_month_date,
                    defaults={
                        'total_salary': teacher.teacher_salary_type.salary,
                        'remaining_salary': teacher.teacher_salary_type.salary,
                        'taken_salary': 0,
                        'total_black_salary': 0,
                        'percentage': 50,
                    }
                )
        month_date = datetime(today.year, today.month, 1)
        exist_salary = TeacherSalary.objects.filter(teacher=teacher, month_date=month_date).exists()
        if not exist_salary:
            if teacher.teacher_salary_type is not None:
                salary, _ = TeacherSalary.objects.get_or_create(
                    teacher=teacher,
                    month_date=month_date,
                    defaults={
                        'total_salary': teacher.teacher_salary_type.salary,
                        'remaining_salary': teacher.teacher_salary_type.salary,
                        'taken_salary': 0,
                        'total_black_salary': 0,
                        'percentage': 50,
                    }
                )
        if teacher.teacher_salary_type and teacher.working_hours:
            if int(teacher.working_hours) != 0:
                salary_month = TeacherSalary.objects.get(teacher=teacher, month_date=month_date)
                worked_hours = working_days_in_month(today.year, today.month)
                stavka = teacher.teacher_salary_type.salary

                salary = (worked_hours / int(teacher.working_hours)) * stavka
                ustama = (salary / 100) * teacher.salary_percentage
                salary = salary + ustama
                salary_month.class_salary = teacher.class_salary
                salary_month.total_salary = salary + teacher.class_salary
                salary_month.remaining_salary = (salary + teacher.class_salary) - salary_month.taken_salary
                salary_month.worked_hours = worked_hours
                salary_month.save()


def teacher_salary_school(salary_id=None, worked_hours=0, class_salary=None, type_salary=False):
    salary_month = TeacherSalary.objects.get(id=salary_id)
    teacher = Teacher.objects.get(id=salary_month.teacher.id)
    worked_days = working_days_in_month(salary_month.month_date.year, salary_month.month_date.month)
    total_days = worked_days - worked_hours

    if type_salary:
        stavka = teacher.teacher_salary_type.salary
        salary = (total_days / int(teacher.working_hours)) * stavka
        ustama = (salary / 100) * teacher.salary_percentage
        salary = salary + ustama
        salary_month.total_salary = salary + teacher.class_salary
        salary_month.remaining_salary = (salary + teacher.class_salary) - salary_month.taken_salary
        salary_month.worked_hours = worked_hours
    else:
        salary_month.total_salary = class_salary
        salary_month.remaining_salary = class_salary - salary_month.taken_salary
        salary_month.class_salary = class_salary

    salary_month.save()
    return salary_month

# 339000
# 678000
# ishlidigan kunla 23
