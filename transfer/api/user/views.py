from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from transfer.api.user.serializers import (
    TransferStaffs, TransferStaffsSalary, UserSalary, UserSalaryList, TransferStaffsSalaryList, TransferUserJobs
)
from user.models import CustomAutoGroup
import time
from transfer.api.user.serializers import TransferUserSerializer
from transfer.api.user.flask_data_base import get_users


def users(self):
    start = time.time()
    list = get_users()
    for info in list:
        serializer = TransferUserSerializer(data=info)
        if serializer.is_valid():
            serializer.save()
        else:
            self.stdout.write(self.style.ERROR(f"Invalid data: {serializer.errors}"))
    end = time.time()
    print(f"Run time users: {(end - start) * 10 ** 3:.03f}ms")
    return True


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
