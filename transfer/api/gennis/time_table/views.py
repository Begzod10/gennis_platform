from rest_framework import generics

from time_table.models import WeekDays
from .serializers import WeekDaysSerializerTransfer, GroupTimeTableSerializerTransfer


class TransferWeekDaysCreate(generics.CreateAPIView):
    queryset = WeekDays.objects.all()
    serializer_class = WeekDaysSerializerTransfer
