from rest_framework import generics

from .serializers import (LocationSerializers, Location)



class CreateLocationList(generics.ListCreateAPIView):
    queryset = Location.objects.all()
    serializer_class = LocationSerializers

    # permission_classes = (IsAuthenticatedOrReadOnly, IsAdminOrReadOnly) # login qilgan yoki yuq ligini va admin emasligini tekshiradi
    #


class LocationRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Location.objects.all()
    serializer_class = LocationSerializers
    # permission_classes = (IsAuthenticatedOrReadOnly, IsAdminOrReadOnly) # login qilgan yoki yuq ligini va admin emasligini tekshiradi
    #
