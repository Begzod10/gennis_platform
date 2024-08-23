from .serializers import TransferAttendancePerMonthSerializer, TransferAttendancePerDaySerializer
from transfer.api.gennis.attendance.flask_data_base import get_AttendancePerMonths, get_attendancedays
import time


def attendance(self):
    start = time.time()
    list = get_AttendancePerMonths()
    for info in list:
        serializer = TransferAttendancePerMonthSerializer(data=info)
        if serializer.is_valid():
            serializer.save()
        else:
            self.stdout.write(self.style.ERROR(f"Invalid data: {serializer.errors}"))
    list = get_attendancedays()
    for info in list:
        serializer = TransferAttendancePerDaySerializer(data=info)
        if serializer.is_valid():
            serializer.save()
        else:
            self.stdout.write(self.style.ERROR(f"Invalid data: {serializer.errors}"))
    end = time.time()
    print(f"Run time attendance: {(end - start) * 10 ** 3:.03f}ms")
    return True

