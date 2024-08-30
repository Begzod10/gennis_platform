from rest_framework import generics

from permissions.response import CustomResponseMixin
from system.models import System
from system.serializers import (
    SystemSerializers
)

from rest_framework.response import Response
from rest_framework import status
class CreateSystem(CustomResponseMixin, generics.CreateAPIView):
    queryset = System.objects.all()
    serializer_class = SystemSerializers


class SystemUpdateAPIView(CustomResponseMixin, generics.UpdateAPIView):
    queryset = System.objects.all()
    serializer_class = SystemSerializers


class SystemDestroyAPIView(CustomResponseMixin, generics.DestroyAPIView):
    queryset = System.objects.all()
    serializer_class = SystemSerializers
    def destroy(self, request, *args, **kwargs):
         super().destroy(request, *args, **kwargs)
         return Response({'message': 'deleted'},status=status.HTTP_200_OK)
