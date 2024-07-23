from rest_framework import generics

from ...models import Hours
from ...serializers import HoursSerializers


class HourListCreateView(generics.ListCreateAPIView):
    queryset = Hours.objects.all()
    serializer_class = HoursSerializers


