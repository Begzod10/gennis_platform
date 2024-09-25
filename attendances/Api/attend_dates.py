import calendar
from datetime import datetime

from rest_framework.response import Response
from rest_framework.views import APIView


class WeekdaysInMonthAPIView(APIView):
    def get(self, request, *args, **kwargs):
        current_date = datetime.now()
        year = current_date.year
        month = current_date.month
        num_days_in_month = calendar.monthrange(year, month)[1]

        weekdays = []

        for day in range(1, num_days_in_month + 1):
            date = datetime(year, month, day)
            if date.weekday() < 5:
                weekdays.append(date.strftime('%d'))

        return Response({
            "month": current_date.strftime('%B'),
            "year": year,
            "weekdays": weekdays
        })
