from datetime import datetime

from Calendar.models import Day
from teachers.models import TeacherSalary


def calculate_teacher_salary(teacher):
    today = datetime.now()
    month = str(today.month).lstrip('0')

    working_days = Day.objects.filter(year__year=today.year, month__month_number=int(month),
                                      type_id__color='green').count()

    month_date = datetime(today.year, today.month, 1)

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

        summ_for_percentage = (teacher.teacher_salary_type.salary * salary.percentage) / 100
        if salary.worked_days:
            overall = (teacher.teacher_salary_type.salary + summ_for_percentage) * (salary.worked_days / working_days)
        else:
            overall = teacher.teacher_salary_type.salary + summ_for_percentage

        if salary.salary_id_salary_list:
            summ = 0
            salaries = salary.salary_id_salary_list.filter(deleted=False).all()
            for salary2 in salaries:
                summ += salary2.salary
            remaining_salary = overall - summ

        else:
            remaining_salary = overall
        salary.remaining_salary = remaining_salary
        salary.total_salary = overall
        salary.save()
