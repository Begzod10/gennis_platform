from rest_framework import generics

from time_table.models import WeekDays
from .serializers import WeekDaysSerializerTransfer, GroupTimeTableSerializerTransfer
import time
from transfer.api.gennis.time_table.flask_data_base import get_group_room_week


def time_table(self):
    start = time.time()
    list = get_group_room_week()
    for info in list:
        serializer = GroupTimeTableSerializerTransfer(data=info)
        if serializer.is_valid():
            serializer.save()
        else:
            self.stdout.write(self.style.ERROR(f"Invalid data: {serializer.errors}"))
    end = time.time()
    print(f"Run time attendance: {(end - start) * 10 ** 3:.03f}ms")
    return True


class TransferWeekDaysCreate(generics.CreateAPIView):
    queryset = WeekDays.objects.all()
    serializer_class = WeekDaysSerializerTransfer
