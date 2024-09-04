from django.core.management.base import BaseCommand
from transfer.api.turon.user.views import users_turon
from transfer.api.turon.teachers.views import teachers_turon
from transfer.api.turon.students.views import students_turon
from transfer.api.turon.classes.views import class_turon
from transfer.api.gennis.run import run2, run4, run6


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        # try:
        #     run2(self)
        #     self.stdout.write(self.style.SUCCESS('Gennis run 2 transfer completed successfully!'))
        # except Exception as e:
        #     self.stdout.write(self.style.ERROR(f'Error during run 2 transfer: {e}'))
        # try:
        #     run4(self)
        #     self.stdout.write(self.style.SUCCESS('Gennis run 4 transfer completed successfully!'))
        # except Exception as e:
        #     self.stdout.write(self.style.ERROR(f'Error during run 4 transfer: {e}'))
        # try:
        #     run6(self)
        #     self.stdout.write(self.style.SUCCESS('Gennis run 6 transfer completed successfully!'))
        # except Exception as e:
        #     self.stdout.write(self.style.ERROR(f'Error during run 6 transfer: {e}'))
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
