from django.utils.timezone import now
# from django_cron import CronJobBase, Schedule
from datetime import date
from attendances.models import AttendancePerMonth
from teachers.models import Teacher, TeacherSalary
from .models import CustomUser, UserSalary


# class CreateMonthly(CronJobBase):
#     RUN_EVERY_MINS = 60 * 24
#     schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
#     code = 'user.create_monthly'
#
#     def do(self):
#         teachers = Teacher.objects.all()
#         for teacher in teachers:
#             current_year = now().year
#             current_month = now().month
#
#             teacher_salary = TeacherSalary.objects.filter(month_date__year=current_year,
#                                                           month_date__month=current_month,
#                                                           teacher=teacher)
#             if not teacher_salary:
#                 attendance = AttendancePerMonth.objects.filter(teacher=teacher,
#                                                                month_date__year=current_year,
#                                                                month_date__month=current_month).first()
#
#                 if attendance:
#                     TeacherSalary.objects.create(
#                         teacher=teacher,
#                         total_salary=attendance.total_salary,
#                         remaining_salary=attendance.remaining_salary,
#                         taken_salary=attendance.taken_salary,
#                         total_black_salary=0,
#                         branch=teacher.user.branch
#                     )


def create_user_salary(user_id):
    user_1 = CustomUser.objects.get(id=user_id)
    for permission in user_1.customautogroup_set.all():
        current_year_old = 2024
        current_month_old = 9
        user_salary_old = UserSalary.objects.filter(date__year=current_year_old, date__month=current_month_old,
                                                    user=user_1)
        if not user_salary_old:
            UserSalary.objects.create(
                user=user_1,
                permission=permission,
                total_salary=permission.salary,
                taken_salary=0,
                remaining_salary=permission.salary,
                date=date(current_year_old, current_month_old, 1)
            )
        else:
            user = UserSalary.objects.get(
                user=user_1,
                permission=permission,
                date__year=current_year_old,
                date__month=current_month_old
            )
            user.total_salary = permission.salary
            user.remaining_salary = permission.salary - int(user.taken_salary)
            user.taken_salary = user.taken_salary
            user.save()
        current_year = now().year
        current_month = now().month
        user_salary = UserSalary.objects.filter(date__year=current_year, date__month=current_month, user=user_1)
        if not user_salary:
            UserSalary.objects.create(
                user=user_1,
                permission=permission,
                total_salary=permission.salary,
                taken_salary=0,
                remaining_salary=permission.salary,
                date=now()
            )
        else:
            user = UserSalary.objects.get(
                user=user_1,
                permission=permission,
                date__year=current_year,
                date__month=current_month
            )
            user.total_salary = permission.salary
            user.remaining_salary = permission.salary - int(user.taken_salary)
            user.taken_salary = user.taken_salary
            user.save()
