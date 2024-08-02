from rest_framework import generics
from location.serializers import LocationSerializers
from location.models import Location


class LocationCreateView(generics.CreateAPIView):
    queryset = Location.objects.all()
    serializer_class = LocationSerializers


class LocationUpdateView(generics.UpdateAPIView):
    queryset = Location.objects.all()
    serializer_class = LocationSerializers


class LocationDestroyView(generics.DestroyAPIView):
    queryset = Location.objects.all()
    serializer_class = LocationSerializers
