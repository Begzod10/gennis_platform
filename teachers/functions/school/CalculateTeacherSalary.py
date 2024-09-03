from datetime import datetime
from Calendar.models import Years, Month, Day
from teachers.models import TeacherSalary, TeacherSalaryType
from django.db.models import Q


def calculate_teacher_salary(teacher):
    today = datetime.now()
    month = str(today.month).lstrip('0')

    working_days = Day.objects.filter(year__year=today.year,month__month_number=int(month)).count()
    month_date = datetime(today.year, today.month, 1)

    date_strp = datetime.strptime(str(month_date), "%Y-%m-%d %H:%M:%S")
    salary, _ = TeacherSalary.objects.get_or_create(
        teacher=teacher,
        month_date__year=date_strp.year,
        month_date__month=date_strp.month,
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

    salary.total_salary = overall
    salary.save()
