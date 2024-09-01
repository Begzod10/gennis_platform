from rest_framework import generics
from rest_framework.exceptions import NotFound
from rest_framework.response import Response

from capital.functions.creat_capital_term import creat_capital_term
from capital.models import Capital, OldCapital
from capital.serializers import (CapitalListSerializers, OldCapitalListSerializers)
from permissions.functions.CheckUserPermissions import check_user_permissions
from permissions.response import CustomResponseMixin
from user.functions.functions import check_auth


class OldCapitalRetrieveAPIView(CustomResponseMixin, generics.RetrieveAPIView):
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


class OldCapitalListView(CustomResponseMixin, generics.ListAPIView):
    queryset = OldCapital.objects.all()
    serializer_class = OldCapitalListSerializers

    def get(self, request, *args, **kwargs):
        user, auth_error = check_auth(request)
        if auth_error:
            return Response(auth_error)

        table_names = ['oldcapital', 'branch', 'paymenttype', 'customuser']
        permissions = check_user_permissions(user, table_names)

        queryset = OldCapital.objects.all()
        location_id = self.request.query_params.get('location_id', None)
        branch_id = self.request.query_params.get('branch_id', None)
        status = self.request.query_params.get('status', None)

        if branch_id is not None:
            queryset = queryset.filter(branch_id=branch_id)
        if location_id is not None:
            queryset = queryset.filter(location_id=location_id)
        if status is not None:
            queryset = queryset.filter(deleted=status)
        serializer = OldCapitalListSerializers(queryset, many=True)
        return Response({'old_capitals': serializer.data, 'permissions': permissions})


class CapitalRetrieveAPIView(CustomResponseMixin, generics.RetrieveAPIView):
    queryset = Capital.objects.all()
    serializer_class = CapitalListSerializers

    def retrieve(self, request, *args, **kwargs):
        # user, auth_error = check_auth(request)
        # if auth_error:
        #     return Response(auth_error)
        #
        # table_names = ['capital', 'branch', 'category', 'paymenttype']
        # permissions = check_user_permissions(user, table_names)
        capital = self.get_queryset()
        capital_data = self.get_serializer(capital, many=True).data
        return Response({'capital': capital_data,})

    def get_queryset(self):
        user_id = self.kwargs.get('pk')
        capital = Capital.objects.filter(category_id=user_id).all()
        return capital
class CapitalRetrieveAPIViewOne(CustomResponseMixin, generics.RetrieveAPIView):
    queryset = Capital.objects.all()
    serializer_class = CapitalListSerializers




class CapitalListView(CustomResponseMixin, generics.ListAPIView):
    queryset = Capital.objects.all()
    serializer_class = CapitalListSerializers

    def get(self, request, *args, **kwargs):
        user, auth_error = check_auth(request)
        if auth_error:
            return Response(auth_error)

        table_names = ['capital', 'branch', 'category', 'paymenttype']
        permissions = check_user_permissions(user, table_names)

        queryset = Capital.objects.all()
        location_id = self.request.query_params.get('location_id', None)
        branch_id = self.request.query_params.get('branch_id', None)

        if branch_id is not None:
            queryset = queryset.filter(branch_id=branch_id)
        if location_id is not None:
            queryset = queryset.filter(location_id=location_id)
        serializer = CapitalListSerializers(queryset, many=True)
        for capital in serializer.data:
            creat_capital_term(capital)
        return Response({'capitals': serializer.data, 'permissions': permissions})
