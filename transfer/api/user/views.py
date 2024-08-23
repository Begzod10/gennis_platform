from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from transfer.api.user.serializers import (
    TransferStaffs, TransferStaffsSalary, TransferUserJobs, TransferStaffsSalaryList
)
from user.models import CustomAutoGroup
import time
from transfer.api.user.flask_data_base import get_users, get_salaries, get_staffsalaries
import random
from user.models import CustomUser
from datetime import datetime


def check_user_name(username):
    username += str(random.randint(1, 10))
    try:
        user = CustomUser.objects.get(username=username)
        if user:
            username += str(random.randint(1, 10))
            username = check_user_name(username)
    except CustomUser.DoesNotExist:
        return username


def validate_and_convert_date(date_str):
    try:
        parsed_date = datetime.strptime(date_str, '%d-%m-%Y')
        return parsed_date.strftime('%Y-%m-%d')
    except ValueError:
        return None


def users(self):
    # start = time.time()
    # list = get_users()
    # for info in list:
    #     serializer = TransferUserSerializer(data=info)
    #     if not serializer.is_valid():
    #         try:
    #             if serializer.errors['username']:
    #                 username = info['username']
    #                 username = check_user_name(username)
    #                 info['username'] = username
    #                 serializer = TransferUserSerializer(data=info)
    #         except KeyError:
    #             if serializer.errors['birth_date']:
    #                 info['birth_date'] = validate_and_convert_date(info['birth_date'])
    #                 serializer = TransferUserSerializer(data=info)
    #     if serializer.is_valid():
    #         serializer.save()
    #     else:
    #         self.stdout.write(self.style.ERROR(f"Invalid data: {serializer.errors}"))
    # end = time.time()
    # print(f"Run time users: {(end - start) * 10 ** 3:.03f}ms")
    start = time.time()
    list = get_salaries()
    for info in list:
        serializer = TransferStaffsSalary(data=info)
        if serializer.is_valid():
            serializer.save()
        else:
            self.stdout.write(self.style.ERROR(f"Invalid data: {serializer.errors}"))
    end = time.time()
    print(f"Run time salary: {(end - start) * 10 ** 3:.03f}ms")
    # start = time.time()
    # list = get_staffsalaries()
    # for info in list:
    #     serializer = TransferStaffsSalaryList(data=info)
    #     if serializer.is_valid():
    #         serializer.save()
    #     else:
    #         self.stdout.write(self.style.ERROR(f"Invalid data: {serializer.errors}"))
    # end = time.time()
    # print(f"Run time salary list: {(end - start) * 10 ** 3:.03f}ms")
    return True


class StaffTransferView(generics.CreateAPIView):
    queryset = CustomAutoGroup.objects.all()
    serializer_class = TransferStaffs


class UserJobsTransfer(generics.GenericAPIView):
    serializer_class = TransferUserJobs

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            teacher = serializer.save()
            return Response({'status': 'role added', 'user_id': teacher.id}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
