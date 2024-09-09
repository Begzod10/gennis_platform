from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from transfer.api.turon.user.serializers import (
    TransferUserSerializer, TransferUserJobs
)
from user.models import CustomAutoGroup
import time
from transfer.api.turon.user.flask_data_base import get_users, get_jobs, get_users_jobs
import random
from user.models import CustomUser
from datetime import datetime
from django.contrib.auth.hashers import make_password
from permissions.serializers import GroupSerializer


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


def users_turon(self):
    start = time.time()
    list = get_jobs()
    for info in list:
        serializer = GroupSerializer(data=info)
        if serializer.is_valid():
            serializer.save()
        else:

            self.stdout.write(self.style.ERROR(f"Invalid data: {serializer.errors}"))

    list = get_users()
    for info in list:
        if info['turon_old_id'] == 258:
            new_password = make_password('1234')
            info['password'] = new_password
            serializer = TransferUserSerializer(data=info)
            if serializer.is_valid():
                serializer.save()
            else:
                print(serializer.errors)
        serializer = TransferUserSerializer(data=info)
        if not serializer.is_valid():
            try:
                if serializer.errors['username']:
                    username = info['username']
                    cleaned_text = username.replace(" ", "")
                    username = check_user_name(cleaned_text)
                    info['username'] = username
                    serializer = TransferUserSerializer(data=info)
                elif serializer.errors['birth_date']:
                    info['birth_date'] = validate_and_convert_date(info['birth_date'])
                    serializer = TransferUserSerializer(data=info)
            except KeyError:
                if serializer.errors['birth_date']:
                    info['birth_date'] = validate_and_convert_date(info['birth_date'])
                    serializer = TransferUserSerializer(data=info)
        if not info['birth_date']:
            info['birth_date'] = None
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

    return True
