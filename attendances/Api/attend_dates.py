import calendar
from datetime import datetime

from rest_framework.response import Response
from rest_framework.views import APIView

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
        students = Student.objects.filter(group_id=group_id)
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
            "students":data
        })
