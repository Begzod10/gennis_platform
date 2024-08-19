from django.core.management.base import BaseCommand
from transfer.api.teacher.uitils import teachers
from transfer.api.user.views import users
from transfer.api.attendance.views import attendance


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        try:
            attendance(self)
            self.stdout.write(self.style.SUCCESS('Attendance data transfer completed successfully!'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error during attendance data transfer: {e}'))
        try:
            users(self)
            self.stdout.write(self.style.SUCCESS('User data transfer completed successfully!'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error during user data transfer: {e}'))
        try:
            teachers(self)
            self.stdout.write(self.style.SUCCESS('Teacher data transfer completed successfully!'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error during teacher data transfer: {e}'))
