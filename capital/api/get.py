from rest_framework import generics
from capital.serializers import (CapitalListSerializers, OldCapitalListSerializers)
from capital.models import Capital, OldCapital
from user.functions.functions import check_auth
from rest_framework.response import Response
from permissions.functions.CheckUserPermissions import check_user_permissions
from capital.functions.creat_capital_term import creat_capital_term


class OldCapitalRetrieveAPIView(generics.RetrieveAPIView):
    queryset = OldCapital.objects.all()
    serializer_class = OldCapitalListSerializers

    def retrieve(self, request, *args, **kwargs):
        user, auth_error = check_auth(request)
        if auth_error:
            return Response(auth_error)

        table_names = ['oldcapital', 'branch', 'paymenttype', 'customuser']
        permissions = check_user_permissions(user, table_names)
        old_capital = self.get_object()
        old_capital_data = self.get_serializer(old_capital).data
        return Response({'old_capital': old_capital_data, 'permissions': permissions})


class OldCapitalListView(generics.ListAPIView):
    queryset = OldCapital.objects.all()
    serializer_class = OldCapitalListSerializers

    def get(self, request, *args, **kwargs):
        user, auth_error = check_auth(request)
        if auth_error:
            return Response(auth_error)

        table_names = ['oldcapital', 'branch', 'paymenttype', 'customuser']
        permissions = check_user_permissions(user, table_names)

        queryset = OldCapital.objects.all()
        serializer = OldCapitalListSerializers(queryset, many=True)
        return Response({'old_capitals': serializer.data, 'permissions': permissions})


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
        for capital in serializer.data:
            creat_capital_term(capital)
        return Response({'capitals': serializer.data, 'permissions': permissions})
