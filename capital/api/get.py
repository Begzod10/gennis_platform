from rest_framework import generics
from capital.serializers import (CapitalListSerializers)
from capital.models import Capital
from user.functions.functions import check_auth
from rest_framework.response import Response
from permissions.functions.CheckUserPermissions import check_user_permissions


class CapitalRetrieveAPIView(generics.RetrieveAPIView):
    queryset = Capital.objects.all()
    serializer_class = CapitalListSerializers

    def retrieve(self, request, *args, **kwargs):
        user, auth_error = check_auth(request)
        if auth_error:
            return Response(auth_error)

        table_names = ['capital', 'branch', 'category', 'paymenttype']
        permissions = check_user_permissions(user, table_names)
        capital = self.get_object()
        capital_data = self.get_serializer(capital).data
        return Response({'capital': capital_data, 'permissions': permissions})


class CapitalListView(generics.ListAPIView):
    queryset = Capital.objects.all()
    serializer_class = CapitalListSerializers

    def get(self, request, *args, **kwargs):
        user, auth_error = check_auth(request)
        if auth_error:
            return Response(auth_error)

        table_names = ['capital', 'branch', 'category', 'paymenttype']
        permissions = check_user_permissions(user, table_names)

        queryset = Capital.objects.all()
        serializer = CapitalListSerializers(queryset, many=True)
        return Response({'capitals': serializer.data, 'permissions': permissions})
