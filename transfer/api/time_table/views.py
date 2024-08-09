from rest_framework import generics

from time_table.models import WeekDays, GroupTimeTable
from .serializers import WeekDaysSerializerTransfer, GroupTimeTableSerializerTransfer


class TransferWeekDaysCreate(generics.CreateAPIView):
    queryset = WeekDays.objects.all()
    serializer_class = WeekDaysSerializerTransfer


class TransferGroupTimeTableCreate(generics.CreateAPIView):
    queryset = GroupTimeTable.objects.all()
    serializer_class = GroupTimeTableSerializerTransfer
