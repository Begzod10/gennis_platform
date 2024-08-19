from django.core.management.base import BaseCommand

from transfer.api.attendance.serializers import TransferAttendancePerMonthSerializer
from transfer.api.teacher.uitils import TeacherDataTransfer
from transfer.api.attendance.views import attendance

from transfer.api.teacher.uitils import teachers


class Command(BaseCommand):
    help = 'Generates and saves attendance per month report'

    def handle(self, *args, **kwargs):
        # attendance(self)
        self.stdout.write(self.style.NOTICE('Starting the teacher data transfer process...'))

        try:
            teachers(self)
            self.stdout.write(self.style.SUCCESS('Teacher data transfer completed successfully!'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error during teacher data transfer: {e}'))
