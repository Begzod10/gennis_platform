from rest_framework import generics
from time_table.models import WeekDays
from time_table.serializers import WeekDaysSerializer


class WeekDaysView(generics.ListAPIView):
    serializer_class = WeekDaysSerializer
    queryset = WeekDays.objects.all()
