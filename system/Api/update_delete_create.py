from rest_framework import generics

from system.models import System
from system.serializers import (
    SystemSerializers
)


class CreateSystem(generics.CreateAPIView):
    queryset = System.objects.all()
    serializer_class = SystemSerializers


class SystemUpdateAPIView(generics.UpdateAPIView):
    queryset = System.objects.all()
    serializer_class = SystemSerializers


class SystemDestroyAPIView(generics.DestroyAPIView):
    queryset = System.objects.all()
    serializer_class = SystemSerializers
