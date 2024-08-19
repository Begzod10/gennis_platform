from django.core.management.base import BaseCommand

from transfer.api.attendance.serializers import TransferAttendancePerMonthSerializer
from transfer.api.teacher.uitils import TeacherDataTransfer
from transfer.api.attendance.views import attendance
from transfer.api.user.views import users

db_url = 'postgresql://postgres:123@localhost:5432/gennis'


class Command(BaseCommand):
    help = 'Generates and saves attendance per month report'

    def handle(self, *args, **kwargs):
        users(self)
        # attendance(self)
