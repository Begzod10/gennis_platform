import logging

from sqlalchemy import create_engine, Table, MetaData, select

from transfer.api.gennis.teacher.salary.serializers import (
    TransferTeacherSalaryCreateSerializers as TransferTeacherSalaryCreateSerializer,
    TransferTeacherSalaryListCreateSerializers as TransferTeacherListCreateSerializer,
    TransferTeacherBlackSalaryCreateSerializers as TransferTeacherBlackSalaryCreateSerializer,
)
from transfer.api.gennis.teacher.serializers import (
    TeacherSerializerTransfer as TransferTeacherSerializer,
    TeacherBranchSerializer as TransferTeacherBranchSerializer,
)


class TeacherDataTransfer:
    def __init__(self, db_url):
        self.engine = create_engine(db_url)
        self.metadata = MetaData()
        self.metadata.reflect(bind=self.engine)
        self._initialize_tables()

    def _initialize_tables(self):
        self.users_table = Table('attendancehistorystudent', self.metadata, autoload_with=self.engine)
        self.month_date_table = Table('calendarmonth', self.metadata, autoload_with=self.engine)
        self.group_table = Table('groups', self.metadata, autoload_with=self.engine)
        self.branches_table = Table('locations', self.metadata, autoload_with=self.engine)
        self.teacher_salary_table = Table('teachersalary', self.metadata, autoload_with=self.engine)
        self.teacher_salaries_table = Table('teachersalaries', self.metadata, autoload_with=self.engine)
        self.teacher_black_salary_table = Table('teacher_black_salary', self.metadata, autoload_with=self.engine)
        self.teachers_table = Table('teachers', self.metadata, autoload_with=self.engine)
        self.month_date = Table('calendarmonth', self.metadata, autoload_with=self.engine)
        self.day_date = Table('calendarday', self.metadata, autoload_with=self.engine)
        self.subjects_table = Table('teacher_subject', self.metadata, autoload_with=self.engine)  # Add this line

    def row_to_dict(self, row, table):
        return {column.name: getattr(row, column.name) for column in table.columns}

    def fetch_single_record(self, table, id):
        try:
            query = select(table).where(table.c.id == int(id))
            with self.engine.connect() as conn:
                result = conn.execute(query).fetchone()
            return self.row_to_dict(result, table) if result else None
        except Exception as e:
            logging.error(f"Error fetching single record from {table.name}: {e}")
            return None

    def fetch_multiple_records(self, table, foreign_key_column, foreign_key_value):
        try:
            query = select(table).where(foreign_key_column == int(foreign_key_value))
            with self.engine.connect() as conn:
                result = conn.execute(query).fetchall()
            return [self.row_to_dict(row, table) for row in result]
        except Exception as e:
            logging.error(f"Error fetching multiple records from {table.name}: {e}")
            return []

    def fetch_teacher_subjects(self, teacher_id):
        try:
            query = select(self.subjects_table).where(self.subjects_table.c.teacher_id == int(teacher_id))
            with self.engine.connect() as conn:
                result = conn.execute(query).fetchall()
            return [row['id'] for row in result]
        except Exception as e:
            logging.error(f"Error fetching subjects for teacher {teacher_id}: {e}")
            return []

    def transfer_teachers(self):
        try:
            with self.engine.connect() as conn:
                teachers_result = conn.execute(self.teachers_table.select()).fetchall()

            for row in teachers_result:
                row_dict = self.row_to_dict(row, self.teachers_table)
                print(row_dict)
                self._transfer_individual_teacher(row_dict)
        except Exception as e:
            logging.error(f"Error transferring teachers: {e}")

    def _transfer_individual_teacher(self, teacher):
        try:
            teacher_data = {
                'old_id': teacher.id,
                'user': teacher.user_id,
                'subject': [subject.id for subject in teacher.subject],
                'color': teacher.table_color,
                'total_students': teacher.total_students,
            }
            serializer = TransferTeacherSerializer(data=teacher_data)
            if serializer.is_valid():
                serializer.save()
                self._transfer_related_data(teacher.id)
            else:
                logging.error(f"Invalid teacher data: {serializer.errors}")

        except Exception as e:
            logging.error(f"Error transferring individual teacher: {e}")

    def _transfer_related_data(self, teacher_id):
        self.transfer_teacher_branches(teacher_id)
        self.transfer_teacher_salaries(teacher_id)
        self.transfer_teacher_salaries_list(teacher_id)
        self.transfer_teacher_black_salaries(teacher_id)

    def get_month(self, id):
        query = select(self.month_date).where(self.month_date.c.id == int(id))
        with self.engine.connect() as conn:
            result = conn.execute(query).fetchone()
        row_dict = dict(zip(self.month_date.columns.keys(), result))
        return row_dict

    def get_day(self, id):
        query = select(self.day_date).where(self.day_date.c.id == int(id))
        with self.engine.connect() as conn:
            result = conn.execute(query).fetchone()
        row_dict = dict(zip(self.day_date.columns.keys(), result))
        return row_dict

    def transfer_teacher_branches(self, teacher_id):
        branches = self.fetch_multiple_records(self.branches_table, self.branches_table.c.id, teacher_id)
        for branch in branches:
            branch_data = {
                "teacher_id": teacher_id,
                "branch_id": branch['id']
            }
            serializer = TransferTeacherBranchSerializer(data=branch_data)
            if serializer.is_valid():
                serializer.save()
            else:
                logging.error(f"Invalid branch data: {serializer.errors}")

    def transfer_teacher_salaries(self, teacher_id):
        salaries = self.fetch_multiple_records(self.teacher_salary_table, self.teacher_salary_table.c.teacher_id,
                                               teacher_id)
        for salary in salaries:
            salary_data = {
                'old_id': salary['id'],
                "teacher": salary['teacher_id'],
                "branch": salary['location_id'],
                "teacher_salary_type": salary.get('salary_type_id'),
                "month_date": self.get_month(salary['calendar_month'])['date'].strftime("%Y-%m-%d"),
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
                logging.error(f"Invalid salary data: {serializer.errors}")

    def transfer_teacher_salaries_list(self, teacher_id):
        salary_list = self.fetch_multiple_records(self.teacher_salaries_table, self.teacher_salaries_table.c.teacher_id,
                                                  teacher_id)
        for salary in salary_list:
            if salary['calendar_day']:
                day = self.get_day(salary['calendar_day'])['date'].strftime("%Y-%m-%d")
            else:
                day = None
                logging.warning(f"Missing 'calendar_day' for salary ID {salary['id']}")

            salary_list_data = {
                "teacher": salary['teacher_id'],
                "salary_id": salary['salary_location_id'],
                "payment": salary['payment_type_id'],
                "branch": salary['location_id'],
                "comment": salary['reason'],
                "deleted": False,
                "salary": salary['payment_sum'],
                "date": day

            }
            serializer = TransferTeacherListCreateSerializer(data=salary_list_data)
            if serializer.is_valid():
                serializer.save()
            else:
                logging.error(f"Invalid salary list data: {serializer.errors}")

    def transfer_teacher_black_salaries(self, teacher_id):
        black_salaries = self.fetch_multiple_records(self.teacher_black_salary_table,
                                                     self.teacher_black_salary_table.c.teacher_id, teacher_id)
        for black_salary in black_salaries:
            self.status_ = {
                "teacher": black_salary['teacher_id'],
                "group": black_salary.get('group_id'),
                "student": black_salary['student_id'],
                "black_salary": black_salary['total_salary'],
                "month_date": self.get_month(black_salary['calendar_month'])['date'].strftime("%Y-%m-%d"),
                "status": black_salary['status']
            }
            black_salary_data = self.status_
            serializer = TransferTeacherBlackSalaryCreateSerializer(data=black_salary_data)
            if serializer.is_valid():
                serializer.save()
            else:
                logging.error(f"Invalid black salary data: {serializer.errors}")


db_url = 'postgresql://postgres:123@localhost:5432/gennis'


def teachers(self):
    teacher_data_transfer = TeacherDataTransfer(db_url)
    # teacher_data_transfer.transfer_teachers()

    self.stdout.write(self.style.NOTICE('Starting the branch and salary transfer process...'))

    try:
        with teacher_data_transfer.engine.connect() as conn:
            teachers_result = conn.execute(teacher_data_transfer.teachers_table.select()).fetchall()

        for row in teachers_result:
            teacher_id = row.id

            teacher_data_transfer.transfer_teacher_branches(teacher_id)
        self.stdout.write(self.style.SUCCESS('Branch  transfer completed successfully!'))
        for row in teachers_result:
            teacher_id = row.id
            teacher_data_transfer.transfer_teacher_salaries(teacher_id)
        self.stdout.write(self.style.SUCCESS('Salary  transfer completed successfully!'))

        for row in teachers_result:
            teacher_id = row.id
            teacher_data_transfer.transfer_teacher_salaries_list(teacher_id)
        self.stdout.write(self.style.SUCCESS('Salary List  transfer completed successfully!'))
        for row in teachers_result:
            teacher_id = row.id

            teacher_data_transfer.transfer_teacher_black_salaries(teacher_id)
        self.stdout.write(self.style.SUCCESS('Black Salary  transfer completed successfully!'))



    except Exception as e:
        self.stdout.write(self.style.ERROR(f'Error during transfer process: {e}'))
