from rest_framework import generics

from ...models import Hours
from ...serializers import HoursSerializers


class HourUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Hours.objects.all()
    serializer_class = HoursSerializers
