
from django.shortcuts import render

# Create your views here.

from rest_framework import generics
from rest_framework.permissions import *

from gennis_platform.permission import IsAdminOrReadOnly
from .serializers import *


class CreateLocationList(generics.ListCreateAPIView):
    queryset = Location.objects.all()
    serializer_class = LocationSerializers
    permission_classes = (IsAuthenticatedOrReadOnly, IsAdminOrReadOnly) # login qilgan yoki yuq ligini va admin emasligini tekshiradi


class LocationRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Location.objects.all()
    serializer_class = LocationSerializers
    permission_classes = (IsAuthenticatedOrReadOnly, IsAdminOrReadOnly) # login qilgan yoki yuq ligini va admin emasligini tekshiradi

