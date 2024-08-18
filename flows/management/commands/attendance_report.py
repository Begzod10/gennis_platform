from django.core.management.base import BaseCommand
from sqlalchemy import create_engine, Table, MetaData, select

from transfer.api.attendance.serializers import TransferAttendancePerMonthSerializer
from transfer.api.teacher.salary.serializers import (
    TransferTeacherSalaryCreateSerializers as TransferTeacherSalaryCreateSerializer,
    TransferTeacherSalaryListCreateSerializers as TransferTeacherListCreateSerializer,
    TransferTeacherBlackSalaryCreateSerializers as TransferTeacherBlackSalaryCreateSerializer,
)
from transfer.api.teacher.serializers import (
    TeacherSerializerTransfer as TransferTeacherSerializer,
    TeacherBranchSerializer as TransferTeacherBranchSerializer,
)


class Command(BaseCommand):
    help = 'Transfers attendance and teacher-related data to the new system'

    def handle(self, *args, **kwargs):
        engine = create_engine('postgresql://postgres:123@localhost:5432/gennis')
        metadata = MetaData()
        metadata.reflect(bind=engine)

        users_table = Table('attendancehistorystudent', metadata, autoload_with=engine)
        month_date_table = Table('calendarmonth', metadata, autoload_with=engine)
        group_table = Table('groups', metadata, autoload_with=engine)
        branches_table = Table('locations', metadata, autoload_with=engine)
        teacher_salary_table = Table('teachersalary', metadata, autoload_with=engine)
        teacher_salaries_table = Table('teachersalaries', metadata, autoload_with=engine)
        teacher_black_salary_table = Table('teacher_black_salary', metadata, autoload_with=engine)
        teachers_table = Table('teachers', metadata, autoload_with=engine)

        def row_to_dict(row, table):
            return {column.name: getattr(row, column.name) for column in table.columns}

        def fetch_single_record(table, id):
            query = select(table).where(table.c.id == int(id))
            with engine.connect() as conn:
                result = conn.execute(query).fetchone()
            return row_to_dict(result, table) if result else None

        def fetch_multiple_records(table, foreign_key_column, foreign_key_value):
            query = select(table).where(foreign_key_column == int(foreign_key_value))
            with engine.connect() as conn:
                result = conn.execute(query).fetchall()
            return [row_to_dict(row, table) for row in result]

        def transfer_teachers():
            with engine.connect() as conn:
                teachers_result = conn.execute(teachers_table.select()).fetchall()

            for row in teachers_result:
                row_dict = row_to_dict(row, teachers_table)

                subject_ids = row_dict.get('subject_ids', [])

                teacher_data = {
                    'old_id': row_dict['id'],
                    'user': row_dict['user_id'],
                    'subject': subject_ids,
                    'color': row_dict['table_color'],
                    'total_students': row_dict['total_students'],
                }
                serializer = TransferTeacherSerializer(data=teacher_data)
                if serializer.is_valid():
                    serializer.save()
                else:
                    self.stdout.write(self.style.ERROR(f"Invalid teacher data: {serializer.errors}"))

                transfer_teacher_branches(row_dict['id'])
                transfer_teacher_salaries(row_dict['id'])
                transfer_teacher_salaries_list(row_dict['id'])
                transfer_teacher_black_salaries(row_dict['id'])

        def transfer_teacher_branches(teacher_id):
            branches = fetch_multiple_records(branches_table, branches_table.c.id, teacher_id)
            for branch in branches:
                branch_data = {
                    "teacher_id": teacher_id,
                    "branch_id": branch['id']
                }
                serializer = TransferTeacherBranchSerializer(data=branch_data)
                if serializer.is_valid():
                    serializer.save()
                else:
                    self.stdout.write(self.style.ERROR(f"Invalid branch data: {serializer.errors}"))

        def transfer_teacher_salaries(teacher_id):
            print("Teacher Salary Table Columns:", [c.name for c in teacher_salary_table.columns])  # Inspect columns
            salaries = fetch_multiple_records(teacher_salary_table, teacher_salary_table.c.teacher_id, teacher_id)
            for salary in salaries:
                salary_data = {
                    'old_id': salary['id'],
                    "teacher": salary['teacher_id'],
                    "branch": salary['location_id'],
                    "teacher_salary_type": salary.get('salary_type_id'),
                    "month_date": salary.get('month_date'),  # Adjust or remove this if necessary
                    "total_salary": salary['total_salary'],
                    "remaining_salary": salary['remaining_salary'],
                    "taken_salary": salary['taken_money'],
                    "total_black_salary": salary.get('total_black_salary', 0),
                    "percentage": salary.get('percentage', 0),
                    "worked_days": salary.get('worked_days', 0)
                }
                serializer = TransferTeacherSalaryCreateSerializer(data=salary_data)
                if serializer.is_valid():
                    serializer.save()
                else:
                    self.stdout.write(self.style.ERROR(f"Invalid salary data: {serializer.errors}"))

        def transfer_teacher_salaries_list(teacher_id):
            salary_list = fetch_multiple_records(teacher_salaries_table, teacher_salaries_table.c.teacher_id, teacher_id)
            for salary in salary_list:
                salary_list_data = {
                    "teacher": salary['teacher_id'],
                    "salary_id": salary['salary_location_id'],
                    "payment": salary['payment_type_id'],
                    "branch": salary['location_id'],
                    "comment": salary['reason'],
                    "deleted": False,
                    "salary": salary['payment_sum']
                }
                serializer = TransferTeacherListCreateSerializer(data=salary_list_data)
                if serializer.is_valid():
                    serializer.save()
                else:
                    self.stdout.write(self.style.ERROR(f"Invalid salary list data: {serializer.errors}"))

        def transfer_teacher_black_salaries(teacher_id):
            black_salaries = fetch_multiple_records(teacher_black_salary_table, teacher_black_salary_table.c.teacher_id, teacher_id)
            for black_salary in black_salaries:
                black_salary_data = {
                    "teacher": black_salary['teacher_id'],
                    "group": black_salary.get('group_id'),
                    "student": black_salary['student_id'],
                    "black_salary": black_salary['total_salary'],
                    "month_date": black_salary.get('month_date'),
                    "status": black_salary['status']
                }
                serializer = TransferTeacherBlackSalaryCreateSerializer(data=black_salary_data)
                if serializer.is_valid():
                    serializer.save()
                else:
                    self.stdout.write(self.style.ERROR(f"Invalid black salary data: {serializer.errors}"))

        def transfer_attendance():
            with engine.connect() as conn:
                attendance_result = conn.execute(users_table.select()).fetchall()

            attendance_list = []
            for row in attendance_result:
                row_dict = row_to_dict(row, users_table)

                group_id = row_dict.get('group_id')
                if group_id is not None:
                    teacher_record = fetch_single_record(group_table, group_id)
                    if teacher_record:
                        teacher_id = teacher_record['teacher_id']
                    else:
                        self.stdout.write(self.style.ERROR(f"No group found for group_id {group_id}"))
                        continue
                else:
                    self.stdout.write(self.style.ERROR(f"Group ID is None for attendance record {row_dict['id']}"))
                    continue

                month_date_record = fetch_single_record(month_date_table, row_dict['calendar_month'])
                if month_date_record:
                    month_date = month_date_record['date'].strftime("%Y-%m-%d")
                else:
                    self.stdout.write(self.style.ERROR(f"No month date found for calendar_month {row_dict['calendar_month']}"))
                    continue

                attendance_data = {
                    'old_id': row_dict['id'],
                    'student': row_dict['student_id'],
                    'teacher': teacher_id,
                    'group': group_id,
                    'total_debt': row_dict['total_debt'],
                    'ball_percentage': row_dict['average_ball'],
                    'remaining_debt': row_dict['remaining_debt'],
                    'payment': row_dict['payment'],
                    'month_date': month_date,
                    'total_charity': row_dict['total_discount'],
                    'system': 1,
                    'absent_days': row_dict['absent_days'],
                    'scored_days': row_dict['scored_days'],
                    'present_days': row_dict['present_days']
                }
                attendance_list.append(attendance_data)

            for data in attendance_list:
                serializer = TransferAttendancePerMonthSerializer(data=data)
                if serializer.is_valid():
                    serializer.save()
                else:
                    self.stdout.write(self.style.ERROR(f"Invalid attendance data: {serializer.errors}"))

        transfer_teachers()
        transfer_attendance()
