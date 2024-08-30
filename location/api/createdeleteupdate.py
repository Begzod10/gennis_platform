from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response

from location.models import Location
from location.serializers import LocationSerializers
from permissions.response import CustomResponseMixin


class LocationCreateView(CustomResponseMixin, generics.CreateAPIView):
    queryset = Location.objects.all()
    serializer_class = LocationSerializers


class LocationUpdateView(CustomResponseMixin, generics.UpdateAPIView):
    queryset = Location.objects.all()
    serializer_class = LocationSerializers


class LocationDestroyView(CustomResponseMixin, generics.DestroyAPIView):
    queryset = Location.objects.all()
    serializer_class = LocationSerializers

    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        return Response({'deleted':"True"}, status=status.HTTP_200_OK)
