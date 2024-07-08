
# Create your views here.

from rest_framework import generics

from .serializers import (
    System, SystemSerializers
)

from django.shortcuts import render






class CreateSystemList(generics.ListCreateAPIView):
    queryset = System.objects.all()
    serializer_class = SystemSerializers
    # permission_classes = (
    #     IsAuthenticatedOrReadOnly, IsAdminOrReadOnly)  # login qilgan yoki yuq ligini va admin emasligini tekshiradi



class SystemRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = System.objects.all()
    serializer_class = SystemSerializers
    # permission_classes = (
    #     IsAuthenticatedOrReadOnly, IsAdminOrReadOnly)  # login qilgan yoki yuq ligini va admin emasligini tekshiradi

