
from datetime import datetime
from Calendar.models import Day
from teachers.models import TeacherSalary, Teacher
from school_time_table.models import ClassTimeTable
from flows.models import Flow
from datetime import date, timedelta, datetime
from django.db.models.functions import TruncDate


def calculate_teacher_salary(teacher):
    today = datetime.now()
    month = str(today.month).lstrip('0')

    working_days = Day.objects.filter(year__year=today.year, month__month_number=int(month),
                                      type_id__color='green').count()

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
            # if salary.total_salary != salary.teacher.teacher_salary_type.salary:
        #     salary.total_salary = salary.teacher.teacher_salary_type.salary
        #     salary.remaining_salary = salary.teacher.teacher_salary_type.salary - salary.taken_salary
        #     salary.save()
        #
        # summ_for_percentage = (teacher.teacher_salary_type.salary * salary.percentage) / 100
        # if salary.worked_hours:
        #     overall = (teacher.teacher_salary_type.salary + summ_for_percentage) * (salary.worked_hours / working_days)
        # else:
        #     overall = teacher.teacher_salary_type.salary + summ_for_percentage
        #
        # if salary.salary_id_salary_list:
        #     summ = 0
        #     salaries = salary.salary_id_salary_list.filter(deleted=False).all()
        #     for salary2 in salaries:
        #         summ += salary2.salary
        #     remaining_salary = overall - summ
        #
        # else:
        #     remaining_salary = overall
        # salary.remaining_salary = remaining_salary
        # salary.total_salary = overall
        # salary.save()

def teacher_salary_school(request=None, update=False, salary_id=None, worked_hours=0, deleted=False, teacher_id=None,
                          month_date=None, class_salary=None):
    if not update:
        if 'flow' in request.data:
            flow = Flow.objects.get(id=request.data['flow'])
            teacher = flow.teacher.id
        else:
            teacher = request.data['teacher']

        # Assuming teacher is already fetched correctly:
        teacher = Teacher.objects.get(id=teacher)

        # Annotate with truncated date in the database and filter based on the truncated date
        time_table_days = ClassTimeTable.objects.filter(teacher=teacher,
                                                        date__month=request.data['date'][5:7],
                                                        date__year=request.data['date'][:4]).distinct('date').count()

        stavka = teacher.teacher_salary_type.salary
        default_hours = 20
        salary = (time_table_days / default_hours) * stavka
        ustama = (salary / 100) * teacher.salary_percentage
        salary = salary + ustama
        month_date = datetime.strptime(request.data['date'][:-3], "%Y-%m")
        TeacherSalary.objects.get_or_create(teacher=teacher, month_date=month_date,
                                            percentage=teacher.salary_percentage)
        salary_month = TeacherSalary.objects.get(teacher=teacher, month_date=month_date)
        salary_month.total_salary = salary
        salary_month.remaining_salary = salary - salary_month.taken_salary
        salary_month.worked_hours = time_table_days
        salary_month.save()
        return salary
    if deleted:
        teacher = Teacher.objects.get(id=teacher_id)
        time_table_days = ClassTimeTable.objects.filter(teacher=teacher,
                                                        date=month_date).order_by('-id').count()

        stavka = teacher.teacher_salary_type.salary
        default_hours = 20
        salary = (time_table_days / default_hours) * stavka
        ustama = (salary / 100) * teacher.salary_percentage
        salary = salary + ustama
        month_date = datetime.strftime(month_date, "%Y-%m-%d")
        month_date = datetime.strptime(month_date[:-3], "%Y-%m")

        salary_month = TeacherSalary.objects.get(teacher=teacher, month_date=month_date)
        salary_month.total_salary = salary
        salary_month.remaining_salary = salary - salary_month.taken_salary
        salary_month.worked_hours = time_table_days
        salary_month.save()
        return salary
    elif not deleted and update:
        teacher = Teacher.objects.get(id=request.id)
        # time_table_hours = ClassTimeTable.objects.filter(teacher=teacher,
        #                                                  date=request.data['date']).order_by('-id').count()
        stavka = teacher.teacher_salary_type.salary
        default_hours = 20
        salary = (worked_hours / default_hours) * stavka
        ustama = (salary / 100) * teacher.salary_percentage
        salary = salary + ustama

        salary_month = TeacherSalary.objects.get(id=salary_id)
        salary_month.class_salary = class_salary
        salary_month.total_salary = salary + class_salary
        salary_month.remaining_salary = (salary + class_salary) - salary_month.taken_salary
        salary_month.worked_hours = worked_hours
        salary_month.save()
        return salary
