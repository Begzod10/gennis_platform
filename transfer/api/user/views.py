from rest_framework import generics

from transfer.api.user.serializers import (
    TransferStaffs, TransferStaffsSalary, UserSalary, UserSalaryList, TransferStaffsSalaryList
)
from user.models import CustomAutoGroup


class StaffTransferView(generics.CreateAPIView):
    queryset = CustomAutoGroup.objects.all()
    serializer_class = TransferStaffs


class StaffSalaryTransferView(generics.CreateAPIView):
    queryset = UserSalary.objects.all()
    serializer_class = TransferStaffsSalary


class StaffSalaryListTransferView(generics.CreateAPIView):
    queryset = UserSalaryList.objects.all()
    serializer_class = TransferStaffsSalaryList
