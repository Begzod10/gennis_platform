import calendar
from datetime import datetime

from rest_framework.response import Response
from rest_framework.views import APIView

from attendances.models import AttendancePerDay
from students.models import Student


class WeekdaysInMonthAPIView(APIView):
    def get(self, request, group_id):
        current_date = datetime.now()
        year = current_date.year
        month = current_date.month
        num_days_in_month = calendar.monthrange(year, month)[1]

        weekdays = []

        for day in range(1, num_days_in_month + 1):
            date = datetime(year, month, day)
            if date.weekday() < 5:
                weekdays.append(date.strftime('%d'))

        attendances = AttendancePerDay.objects.filter(day=current_date, group=group_id).values_list('student_id',
                                                                                                    flat=True)

        students = Student.objects.filter(groups_student=group_id).exclude(id__in=attendances).all()

        data = []

        for student in students:
            data.append({
                "id": student.id,
                "name": student.user.name,
                "surname": student.user.surname,
            })

        return Response({
            "month": current_date.strftime('%B'),
            "year": year,
            "weekdays": weekdays,
            "students": data
        })
