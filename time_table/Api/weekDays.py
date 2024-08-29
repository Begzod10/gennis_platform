from rest_framework import generics
from time_table.models import WeekDays
from time_table.serializers import WeekDaysSerializer
from rest_framework.response import Response
from datetime import datetime


class WeekDaysView(generics.ListAPIView):
    serializer_class = WeekDaysSerializer
    queryset = WeekDays.objects.all()

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        today = datetime.now()
        day_name = today.strftime('%A')
        week_day = WeekDays.objects.get(name_en=day_name)
        data = {
            'days': response.data,
            'today': week_day.pk
        }
        return Response(data)
