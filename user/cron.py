from django.utils.timezone import now
from django_cron import CronJobBase, Schedule

from attendances.models import AttendancePerMonth
from teachers.models import Teacher, TeacherSalary
from .models import CustomUser, UserSalary


class CreateMonthly(CronJobBase):
    RUN_EVERY_MINS = 60 * 24
    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'user.create_monthly'

    def do(self):
        teachers = Teacher.objects.all()
        for teacher in teachers:
            current_year = now().year
            current_month = now().month

            teacher_salary = TeacherSalary.objects.filter(month_date__year=current_year,
                                                          month_date__month=current_month,
                                                          teacher=teacher)
            if not teacher_salary:
                attendance = AttendancePerMonth.objects.filter(teacher=teacher,
                                                               month_date__year=current_year,
                                                               month_date__month=current_month).first()

                if attendance:
                    TeacherSalary.objects.create(
                        teacher=teacher,
                        total_salary=attendance.total_salary,
                        remaining_salary=attendance.remaining_salary,
                        taken_salary=attendance.taken_salary,
                        total_black_salary=0,
                        branch=teacher.user.branch
                    )


def create_user_salary(user_id):
    print(user_id)
    user = CustomUser.objects.get(id=user_id)
    for permission in user.customautogroup_set.all():
        current_year = now().year
        current_month = now().month
        user_salary = UserSalary.objects.filter(date__year=current_year, date__month=current_month, user=user)
        if not user_salary:
            UserSalary.objects.create(
                user=user,
                permission=permission,
                total_salary=permission.salary,
                taken_salary=0,
                remaining_salary=permission.salary,
                date=now()
            )
        else:
            user = UserSalary.objects.get(
                user=user,
                permission=permission,
                date__year=current_year,
                date__month=current_month
            )
            user.total_salary = permission.salary
            user.remaining_salary = permission.salary - int(user.taken_salary)
            user.taken_salary = user.taken_salary
            user.save()
