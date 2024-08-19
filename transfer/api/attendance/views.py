from rest_framework import generics
from rest_framework.response import Response

from group.serializers import GroupSerializer
from attendances.models import AttendancePerMonth, AttendancePerDay
from attendances.serializers import AttendancePerMonthSerializer, AttendancePerDaySerializer
from .serializers import TransferAttendancePerMonthSerializer, TransferAttendancePerDaySerializer
from transfer.api.attendance.flask_data_base import get_AttendancePerMonths


def attendance(self):
    list = get_AttendancePerMonths()
    for info in list:
        serializer = TransferAttendancePerMonthSerializer(data=info)
        if serializer.is_valid():
            serializer.save()
        else:
            self.stdout.write(self.style.ERROR(f"Invalid data: {serializer.errors}"))


class TransferCreatAttendancePerMonth(generics.ListCreateAPIView):
    queryset = AttendancePerMonth.objects.all()
    serializer_class = TransferAttendancePerMonthSerializer

    def create(self, request, *args, **kwargs):
        write_serializer = self.get_serializer(data=request.data, partial=True)
        write_serializer.is_valid(raise_exception=True)
        self.perform_create(write_serializer)

        instance = AttendancePerMonth.objects.get(pk=write_serializer.data['id'])
        read_serializer = AttendancePerMonthSerializer(instance)
        return Response(read_serializer.data)


class TransferCreatAttendancePerDay(generics.ListCreateAPIView):
    queryset = AttendancePerDay.objects.all()
    serializer_class = TransferAttendancePerDaySerializer

    def create(self, request, *args, **kwargs):
        write_serializer = self.get_serializer(data=request.data, partial=True)
        write_serializer.is_valid(raise_exception=True)
        self.perform_create(write_serializer)
        instance = AttendancePerDay.objects.get(pk=write_serializer.data['id'])
        read_serializer = AttendancePerDaySerializer(instance)
        return Response(read_serializer.data)

# from rest_framework import generics
# from attendances.models import AttendancePerMonth, AttendancePerDay
# from .serializers import TransferAttendancePerMonthSerializer, TransferAttendancePerDaySerializer
#
#
# class AttendancePerDayCreateView(generics.CreateAPIView):
#     queryset = AttendancePerDay.objects.all()
#     serializer_class = TransferAttendancePerDaySerializer
#
#
# class AttendancePerMonthCreateView(generics.CreateAPIView):
#     queryset = AttendancePerMonth.objects.all()
#     serializer_class = TransferAttendancePerMonthSerializer
