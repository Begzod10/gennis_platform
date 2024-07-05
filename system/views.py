from django.shortcuts import render

# Create your views here.

from rest_framework import generics
from rest_framework.permissions import *

from gennis_platform.permission import IsAdminOrReadOnly
from .serializers import *


class CreateSystemList(generics.ListCreateAPIView):
    queryset = System.objects.all()
    serializer_class = SystemSerializers
    permission_classes = (
        IsAuthenticatedOrReadOnly, IsAdminOrReadOnly)  # login qilgan yoki yuq ligini va admin emasligini tekshiradi


class SystemRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = System.objects.all()
    serializer_class = SystemSerializers
    permission_classes = (
        IsAuthenticatedOrReadOnly, IsAdminOrReadOnly)  # login qilgan yoki yuq ligini va admin emasligini tekshiradi
