from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response

from transfer.api.user.serializers import (
    TransferStaffs, TransferStaffsSalary, UserSalary, UserSalaryList, TransferStaffsSalaryList, TransferUserJobs
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


class UserJobsTransfer(generics.GenericAPIView):
    serializer_class = TransferUserJobs

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            teacher = serializer.save()
            return Response({'status': 'role added', 'user_id': teacher.id}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
