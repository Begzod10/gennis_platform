from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from transfer.api.gennis.user.serializers import (
    TransferStaffs, TransferStaffsSalary, TransferUserJobs, TransferStaffsSalaryList, TransferUserSerializer
)
from user.models import CustomAutoGroup
import time
from transfer.api.gennis.user.flask_data_base import get_salaries, get_users_jobs, get_staffsalaries, get_jobs, \
    get_users
import random
from user.models import CustomUser
from datetime import datetime
from permissions.serializers import GroupSerializer
from transfer.api.gennis.students.flask_data_base import get_students, get_deleted_students, get_studenthistorygroups, \
    get_studentcharity, get_studentpayments
import time
from transfer.api.gennis.students.serializers import StudentSerializerTransfer, TransferDeletedNewStudentSerializer, \
    StudentHistoryGroupCreateSerializerTransfer, StudentCharitySerializerTransfer
from transfer.api.gennis.students.payments.serializers import StudentPaymentSerializerTransfer
from transfer.api.gennis.group.serializers import TransferGroupCreateUpdateSerializer
from transfer.api.gennis.group.flask_data_base import get_groups
import time
from transfer.api.gennis.attendance.serializers import TransferAttendancePerMonthSerializer, \
    TransferAttendancePerDaySerializer
from transfer.api.gennis.attendance.flask_data_base import get_AttendancePerMonths, get_attendancedays
import time
from transfer.api.gennis.teacher.uitils import teachers
from transfer.api.gennis.overhead.serializers import TransferOverheadSerializerCreate
from transfer.api.gennis.overhead.flask_data_base import get_overheads
import time
from rest_framework import generics
from time_table.functions.creatWeekDays import creat_week_days
from time_table.models import WeekDays
from transfer.api.gennis.time_table.serializers import WeekDaysSerializerTransfer, GroupTimeTableSerializerTransfer
import time
from transfer.api.gennis.time_table.flask_data_base import get_group_room_week


def check_user_name(username):
    user = CustomUser.objects.filter(username=username).first()
    if user:
        username = f'{username}{str(random.randint(1, 10))}'
        check_user_name(username)
    else:
        return username


def validate_and_convert_date(date_str):
    try:
        parsed_date = datetime.strptime(date_str, '%d-%m-%Y')
        return parsed_date.strftime('%Y-%m-%d')
    except ValueError:
        return None


def run2(self):
    list = get_jobs()
    for info in list:
        serializer = GroupSerializer(data=info)
        if serializer.is_valid():
            serializer.save()
        else:
            self.stdout.write(self.style.ERROR(f"Invalid data: {serializer.errors}"))

    list = get_users()
    for info in list:
        serializer = TransferUserSerializer(data=info)
        if not serializer.is_valid():
            try:
                if serializer.errors['username']:
                    username = info['username']
                    cleaned_text = username.replace(" ", "")
                    username = check_user_name(cleaned_text)
                    info['username'] = username
                    serializer = TransferUserSerializer(data=info)
            except KeyError:
                if serializer.errors['birth_date']:
                    info['birth_date'] = validate_and_convert_date(info['birth_date'])
                    serializer = TransferUserSerializer(data=info)
        if serializer.is_valid():
            serializer.save()
        else:
            self.stdout.write(self.style.ERROR(f"Invalid data: {serializer.errors}"))

    list = get_users_jobs()
    for info in list:
        serializer = TransferUserJobs(data=info)
        if serializer.is_valid():
            serializer.save()
        else:
            self.stdout.write(self.style.ERROR(f"Invalid data: {serializer.errors}"))

    list = get_students()
    for info in list:
        serializer = StudentSerializerTransfer(data=info)
        if serializer.is_valid():
            serializer.save()
        else:
            self.stdout.write(self.style.ERROR(f"Invalid data: {serializer.errors}"))

    list = get_deleted_students()
    for info in list:
        serializer = TransferDeletedNewStudentSerializer(data=info)
        if serializer.is_valid():
            serializer.save()
        else:
            self.stdout.write(self.style.ERROR(f"Invalid data: {serializer.errors}"))
    return True


def run4(self):

    list = get_groups()
    for info in list:
        serializer = TransferGroupCreateUpdateSerializer(data=info)
        if serializer.is_valid():
            serializer.save()
        else:
            self.stdout.write(self.style.ERROR(f"Invalid data: {serializer.errors}"))


    list = get_AttendancePerMonths()
    for info in list:
        serializer = TransferAttendancePerMonthSerializer(data=info)
        if serializer.is_valid():
            serializer.save()
        else:
            self.stdout.write(self.style.ERROR(f"Invalid data: {serializer.errors}"))

    list = get_attendancedays()
    for info in list:
        serializer = TransferAttendancePerDaySerializer(data=info)
        if serializer.is_valid():
            serializer.save()
        else:
            self.stdout.write(self.style.ERROR(f"Invalid data: {serializer.errors}"))

    list = get_studentpayments()
    for info in list:
        serializer = StudentPaymentSerializerTransfer(data=info)
        if serializer.is_valid():
            serializer.save()
        else:
            self.stdout.write(self.style.ERROR(f"Invalid data: {serializer.errors}"))


    list = get_studentcharity()
    for info in list:
        serializer = StudentCharitySerializerTransfer(data=info)
        if serializer.is_valid():
            serializer.save()
        else:
            self.stdout.write(self.style.ERROR(f"Invalid data: {serializer.errors}"))
    list = get_studenthistorygroups()
    for info in list:
        serializer = StudentHistoryGroupCreateSerializerTransfer(data=info)
        if serializer.is_valid():
            serializer.save()
        else:
            self.stdout.write(self.style.ERROR(f"Invalid data: {serializer.errors}"))

    try:
        teachers(self)
        self.stdout.write(self.style.SUCCESS('Gennis Teacher data transfer completed successfully!'))
    except Exception as e:
        self.stdout.write(self.style.ERROR(f'Error during gennis teacher data transfer: {e}'))

    list = get_overheads()
    for info in list:
        serializer = TransferOverheadSerializerCreate(data=info)
        if serializer.is_valid():
            serializer.save()
        else:
            self.stdout.write(self.style.ERROR(f"Invalid data: {serializer.errors}"))

    return True


def run6(self):
    list = get_group_room_week()
    creat_week_days()
    for info in list:
        serializer = GroupTimeTableSerializerTransfer(data=info)
        if serializer.is_valid():
            serializer.save()
        else:
            self.stdout.write(self.style.ERROR(f"Invalid data: {serializer.errors}"))
    list = get_salaries()
    for info in list:
        serializer = TransferStaffsSalary(data=info)
        if serializer.is_valid():
            serializer.save()
        else:
            self.stdout.write(self.style.ERROR(f"Invalid data: {serializer.errors}"))
    list = get_staffsalaries()
    for info in list:
        serializer = TransferStaffsSalaryList(data=info)
        if serializer.is_valid():
            serializer.save()
        else:
            self.stdout.write(self.style.ERROR(f"Invalid data: {serializer.errors}"))
    return True

# def run4(self):
#     return True
