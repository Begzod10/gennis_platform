from django.core.management.base import BaseCommand
from transfer.api.attendance.serializers import TransferAttendancePerMonthSerializer
from transfer.api.attendance.flask_data_base import get_AttendancePerMonths
from transfer.api.user.flask_data_base import get_users


class Command(BaseCommand):
    help = 'Generates and saves attendance per month report'

    def handle(self, *args, **kwargs):
        # list = get_users()
        list = get_AttendancePerMonths()
        for info in list:
            serializer = TransferAttendancePerMonthSerializer(data=info)
            if serializer.is_valid():
                serializer.save()
            else:
                self.stdout.write(self.style.ERROR(f"Invalid data: {serializer.errors}"))
