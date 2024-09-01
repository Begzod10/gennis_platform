from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import System
from .serializers import (
    SystemSerializers
)


class CreateSystemList(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = System.objects.all()
    serializer_class = SystemSerializers

    def get(self, request, *args, **kwargs):
        queryset = System.objects.all()
        serializer = SystemSerializers(queryset, many=True)
        return Response(serializer.data)


class SystemRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    queryset = System.objects.all()
    serializer_class = SystemSerializers

    def retrieve(self, request, *args, **kwargs):
        system = self.get_object()
        system_data = self.get_serializer(system).data
        return Response(system_data, )
