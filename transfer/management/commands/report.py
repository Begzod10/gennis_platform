from django.core.management.base import BaseCommand

from transfer.api.gennis.overhead.views import overhead
from transfer.api.turon.user.views import users_turon
from transfer.api.turon.teachers.views import teachers_turon
from transfer.api.turon.students.views import students_turon
from transfer.api.turon.classes.views import class_turon
from transfer.api.gennis.time_table.views import time_table
from transfer.api.gennis.group.views import groups
from transfer.api.gennis.user.views import users
from transfer.api.gennis.students.views import students
from transfer.api.gennis.attendance.views import attendance
from transfer.api.gennis.teacher.uitils import teachers


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        try:
            users_turon(self)
            self.stdout.write(self.style.SUCCESS('Turon User data transfer completed successfully!'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error during turon user data transfer: {e}'))
        # try:
        #     teachers_turon(self)
        #     self.stdout.write(self.style.SUCCESS('Turon Teachers data transfer completed successfully!'))
        # except Exception as e:
        #     self.stdout.write(self.style.ERROR(f'Error during turon teachers data transfer: {e}'))
        # try:
        #     students_turon(self)
        #     self.stdout.write(self.style.SUCCESS('Turon Students data transfer completed successfully!'))
        # except Exception as e:
        #     self.stdout.write(self.style.ERROR(f'Error during turon students data transfer: {e}'))
        # try:
        #     class_turon(self)
        #     self.stdout.write(self.style.SUCCESS('Turon Class data transfer completed successfully!'))
        # except Exception as e:
        #     self.stdout.write(self.style.ERROR(f'Error during turon class data transfer: {e}'))
        # try:
        #     overhead(self)
        #     self.stdout.write(self.style.SUCCESS('Gennis Overhead data transfer completed successfully!'))
        # except Exception as e:
        #     self.stdout.write(self.style.ERROR(f'Error during gennis overhead data transfer: {e}'))
        # try:
        #     time_table(self)
        #     self.stdout.write(self.style.SUCCESS('Gennis Time table data transfer completed successfully!'))
        # except Exception as e:
        #     self.stdout.write(self.style.ERROR(f'Error during gennis time table data transfer: {e}'))
        # try:
        #     groups(self)
        #     self.stdout.write(self.style.SUCCESS('Gennis Groups data transfer completed successfully!'))
        # except Exception as e:
        #     self.stdout.write(self.style.ERROR(f'Error during gennis groups data transfer: {e}'))
        # try:
        #     students(self)
        #     self.stdout.write(self.style.SUCCESS('Gennis Students data transfer completed successfully!'))
        # except Exception as e:
        #     self.stdout.write(self.style.ERROR(f'Error during gennis students data transfer: {e}'))
        # try:
        #     attendance(self)
        #     self.stdout.write(self.style.SUCCESS('Gennis Attendance data transfer completed successfully!'))
        # except Exception as e:
        #     self.stdout.write(self.style.ERROR(f'Error during gennis attendance data transfer: {e}'))
        # try:
        #     users(self)
        #     self.stdout.write(self.style.SUCCESS('Gennis User data transfer completed successfully!'))
        # except Exception as e:
        #     self.stdout.write(self.style.ERROR(f'Error during gennis user data transfer: {e}'))
        # try:
        #     teachers(self)
        #     self.stdout.write(self.style.SUCCESS('Gennis Teacher data transfer completed successfully!'))
        # except Exception as e:
        #     self.stdout.write(self.style.ERROR(f'Error during gennis teacher data transfer: {e}'))
