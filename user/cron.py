from django_cron import CronJobBase, Schedule
from .models import CustomUser, UserSalary, CustomPermission
from django.utils.timezone import now


class CreateMonthly(CronJobBase):
    RUN_EVERY_MINS = 60 * 24
    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'user.create_monthly'

    def do(self):
        users = CustomUser.objects.all()
        for user in users:
            for permission in user.user_permissions.all():
                current_year = now().year
                current_month = now().month
                user_salary = UserSalary.objects.filter(date__year=current_year, date__month=current_month, user=user)
                if not user_salary:
                    UserSalary.objects.create(
                        user=user,
                        permission=permission.custom_permission,
                        total_salary=permission.custom_permission.salary,
                        taken_salary=0,
                        remaining_salary=permission.custom_permission.salary
                    )

