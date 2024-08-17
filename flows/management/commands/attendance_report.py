from django.core.management.base import BaseCommand
from sqlalchemy import create_engine, Table, MetaData, select

from transfer.api.attendance.serializers import TransferAttendancePerMonthSerializer


class Command(BaseCommand):
    help = 'Generates and saves attendance per month report'

    def handle(self, *args, **kwargs):
        engine = create_engine('postgresql://postgres:123@localhost:5432/gennis')

        metadata = MetaData()
        metadata.reflect(bind=engine)
        users = Table('attendancehistorystudent', metadata, autoload_with=engine)
        month_date = Table('calendarmonth', metadata, autoload_with=engine)
        group = Table('groups', metadata, autoload_with=engine)

        def get_month(id):
            query = select(month_date).where(month_date.c.id == int(id))
            with engine.connect() as conn:
                result = conn.execute(query).fetchone()
            row_dict = dict(zip(month_date.columns.keys(), result))
            return row_dict

        def get_group(id):
            query = select(group).where(group.c.id == int(id))
            with engine.connect() as conn:
                result = conn.execute(query).fetchone()
            row_dict = dict(zip(group.columns.keys(), result))
            return row_dict

        with engine.connect() as conn:
            result = conn.execute(users.select()).fetchall()

        def get_AttendancePerMonths():
            list = []
            for row in result:
                row_dict = dict(zip(users.columns.keys(), row))
                if row_dict['group_id']:
                    info = {
                        'old_id': row_dict['id'],
                        'student': row_dict['student_id'],
                        'teacher': get_group(row_dict['group_id'])['teacher_id'],
                        'group': row_dict['group_id'],
                        'total_debt': row_dict['total_debt'],
                        'ball_percentage': row_dict['average_ball'],
                        'remaining_debt': row_dict['remaining_debt'],
                        'payment': row_dict['payment'],
                        'month_date': get_month(row_dict['calendar_month'])['date'].strftime("%Y-%m-%d"),
                        'total_charity': row_dict['total_discount'],
                        'system': 1,
                        'absent_days': row_dict['absent_days'],
                        'scored_days': row_dict['scored_days'],
                        'present_days': row_dict['present_days']
                    }
                    list.append(info)
            return list

        list = get_AttendancePerMonths()
        for info in list:
            serializer = TransferAttendancePerMonthSerializer(data=info)
            if serializer.is_valid():
                serializer.save()
            else:
                self.stdout.write(self.style.ERROR(f"Invalid data: {serializer.errors}"))
