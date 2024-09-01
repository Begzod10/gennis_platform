from rest_framework import generics
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from permissions.response import CustomResponseMixin
from system.models import System
from system.serializers import (
    SystemSerializers
)


class CreateSystem(CustomResponseMixin, generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = System.objects.all()
    serializer_class = SystemSerializers


class SystemUpdateAPIView(CustomResponseMixin, generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = System.objects.all()
    serializer_class = SystemSerializers


class SystemDestroyAPIView(CustomResponseMixin, generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]
    queryset = System.objects.all()
    serializer_class = SystemSerializers

    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        return Response({'message': 'deleted'}, status=status.HTTP_200_OK)
