from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from transfer.api.gennis.user.serializers import (
    TransferStaffs, TransferStaffsSalary, TransferUserJobs, TransferStaffsSalaryList, TransferUserSerializer
)
from user.models import CustomAutoGroup
import time
from transfer.api.gennis.user.flask_data_base import get_salaries, get_users_jobs, get_staffsalaries, get_jobs, get_users
import random
from user.models import CustomUser
from datetime import datetime
from permissions.serializers import GroupSerializer


def users(self):

    return True


class StaffTransferView(generics.CreateAPIView):
    queryset = CustomAutoGroup.objects.all()
    serializer_class = TransferStaffs
