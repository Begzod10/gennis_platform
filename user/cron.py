from django_cron import CronJobBase, Schedule
from .models import CustomUser, UserSalary
from datetime import datetime


class CreateMonthlyUsersAndPermissionsJob(CronJobBase):
    # RUN_EVERY_MINS = 60 * 24 * 30
    RUN_EVERY_MINS = 1


    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'user.create_monthly_users_and_permissions'

    def do(self):
        current_month = datetime.now().strftime('%Y-%m')
        users = CustomUser.objects.all()
        print(users)
        for user in users:
            UserSalary.objects.get_or_create(user=user, data=current_month,
                                             permission=user.user_permissions.CustomPermission,
                                             total_salary=user.user_permissions.CustomPermission.salary,
                                             taken_salary=0,
                                             remaining_salary=user.user_permissions.CustomPermission.salary)
