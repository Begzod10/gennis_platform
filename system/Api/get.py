from rest_framework import generics
from system.serializers import (
    SystemSerializers
)
from system.models import System
from user.functions.functions import check_auth
from rest_framework.response import Response
from permissions.functions.CheckUserPermissions import check_user_permissions
from transfer.flask_data_base import get_AttendancePerMonths
from rest_framework.renderers import JSONRenderer
from attendances.models import AttendancePerMonth
from attendances.serializers import AttendancePerMonthSerializer
from transfer.api.attendance.serializers import TransferAttendancePerMonthSerializer


class SystemList(generics.ListAPIView):
    queryset = System.objects.all()
    serializer_class = SystemSerializers

    def get(self, request, *args, **kwargs):
        user, auth_error = check_auth(request)
        if auth_error:
            return Response(auth_error)

        table_names = ['system']
        permissions = check_user_permissions(user, table_names)

        # list = get_AttendancePerMonths()
        # for info in list:
        #     serializer = TransferAttendancePerMonthSerializer(data=info)
        #     if serializer.is_valid():
        #         serializer.save()


        queryset = System.objects.all()
        serializer = SystemSerializers(queryset, many=True)
        return Response({'systems': serializer.data, 'permissions': permissions})


class SystemRetrieveAPIView(generics.RetrieveAPIView):
    queryset = System.objects.all()
    serializer_class = SystemSerializers

    def retrieve(self, request, *args, **kwargs):
        user, auth_error = check_auth(request)
        if auth_error:
            return Response(auth_error)

        table_names = ['system']
        permissions = check_user_permissions(user, table_names)
        system = self.get_object()
        system_data = self.get_serializer(system).data
        return Response({'system': system_data, 'permissions': permissions})
