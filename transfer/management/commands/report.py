from django.core.management.base import BaseCommand

from transfer.api.teacher.uitils import TeacherDataTransfer
from transfer.api.user.flask_data_base import get_users

db_url = 'postgresql://postgres:123@localhost:5432/gennis'


class Command(BaseCommand):
    help = 'Generates and saves attendance per month report'

    def handle(self, *args, **kwargs):
        teacher_data_transfer = TeacherDataTransfer(db_url)

        self.stdout.write(self.style.NOTICE('Starting the branch and salary transfer process...'))

        try:
            with teacher_data_transfer.engine.connect() as conn:
                teachers_result = conn.execute(teacher_data_transfer.teachers_table.select()).fetchall()

            for row in teachers_result:
                teacher_id = row.id

                teacher_data_transfer.transfer_teacher_branches(teacher_id)
                teacher_data_transfer.transfer_teacher_salaries(teacher_id)
                teacher_data_transfer.transfer_teacher_salaries_list(teacher_id)
                teacher_data_transfer.transfer_teacher_black_salaries(teacher_id)

            self.stdout.write(self.style.SUCCESS('Branch and salary transfer completed successfully!'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error during transfer process: {e}'))
        list = get_users()
        # list = get_AttendancePerMonths()
        # for info in list:
        #     serializer = TransferAttendancePerMonthSerializer(data=info)
        #     if serializer.is_valid():
        #         serializer.save()
        #     else:
        #         self.stdout.write(self.style.ERROR(f"Invalid data: {serializer.errors}"))
