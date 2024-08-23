from django.core.management.base import BaseCommand

from transfer.api.attendance.views import attendance
from transfer.api.group.views import groups
from transfer.api.students.views import students
from transfer.api.teacher.uitils import teachers
from transfer.api.user.views import users
from transfer.api.time_table.views import time_table
from transfer.api.overhead.views import overhead


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        # try:
        #     overhead(self)
        #     self.stdout.write(self.style.SUCCESS('Overhead data transfer completed successfully!'))
        # except Exception as e:
        #     self.stdout.write(self.style.ERROR(f'Error during overhead data transfer: {e}'))
        # try:
        #     time_table(self)
        #     self.stdout.write(self.style.SUCCESS('Time table data transfer completed successfully!'))
        # except Exception as e:
        #     self.stdout.write(self.style.ERROR(f'Error during time table data transfer: {e}'))
        # try:
        #     groups(self)
        #     self.stdout.write(self.style.SUCCESS('Groups data transfer completed successfully!'))
        # except Exception as e:
        #     self.stdout.write(self.style.ERROR(f'Error during groups data transfer: {e}'))
        # try:
        #     students(self)
        #     self.stdout.write(self.style.SUCCESS('Students data transfer completed successfully!'))
        # except Exception as e:
        #     self.stdout.write(self.style.ERROR(f'Error during students data transfer: {e}'))
        # try:
        #     attendance(self)
        #     self.stdout.write(self.style.SUCCESS('Attendance data transfer completed successfully!'))
        # except Exception as e:
        #     self.stdout.write(self.style.ERROR(f'Error during attendance data transfer: {e}'))
        try:
            users(self)
            self.stdout.write(self.style.SUCCESS('User data transfer completed successfully!'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error during user data transfer: {e}'))
        # try:
        #     teachers(self)
        #     self.stdout.write(self.style.SUCCESS('Teacher data transfer completed successfully!'))
        # except Exception as e:
        #     self.stdout.write(self.style.ERROR(f'Error during teacher data transfer: {e}'))
