from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from system.models import System
from system.serializers import (
    SystemSerializers
)


class SystemList(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = System.objects.all()
    serializer_class = SystemSerializers

    def get(self, request, *args, **kwargs):
        # list = get_AttendancePerMonths()
        # for info in list:
        #     serializer = TransferAttendancePerMonthSerializer(data=info)
        #     if serializer.is_valid():
        #         serializer.save()

        queryset = System.objects.all()
        serializer = SystemSerializers(queryset, many=True)
        return Response(serializer.data)


class SystemRetrieveAPIView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    queryset = System.objects.all()
    serializer_class = SystemSerializers

    def retrieve(self, request, *args, **kwargs):
        system = self.get_object()
        system_data = self.get_serializer(system).data
        return Response(system_data)
