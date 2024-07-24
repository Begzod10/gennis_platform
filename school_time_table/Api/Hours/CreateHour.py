from rest_framework import generics
from rest_framework.response import Response

from ...models import Hours, ClassTimeTable
from ...serializers import HoursSerializers, ClassTimeTableCreateUpdateSerializers, ClassTimeTableReadSerializers


class HourListCreateView(generics.ListCreateAPIView):
    queryset = Hours.objects.all()
    serializer_class = HoursSerializers


