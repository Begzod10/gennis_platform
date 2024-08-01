from payments.serializers import (PaymentTypesSerializers)
from rest_framework import generics
from payments.models import PaymentTypes
from user.functions.functions import check_auth
from rest_framework.response import Response
from permissions.functions.CheckUserPermissions import check_user_permissions


class PaymentTypesList(generics.ListAPIView):
    queryset = PaymentTypes.objects.all()
    serializer_class = PaymentTypesSerializers

    def get(self, request, *args, **kwargs):
        user, auth_error = check_auth(request)
        if auth_error:
            return Response(auth_error)

        table_names = ['paymenttypes']
        permissions = check_user_permissions(user, table_names)

        queryset = PaymentTypes.objects.all()
        serializer = PaymentTypesSerializers(queryset, many=True)
        return Response({'paymenttypes': serializer.data, 'permissions': permissions})


class PaymentTypesRetrieveAPIView(generics.RetrieveAPIView):
    queryset = PaymentTypes.objects.all()
    serializer_class = PaymentTypesSerializers

    def retrieve(self, request, *args, **kwargs):
        user, auth_error = check_auth(request)
        if auth_error:
            return Response(auth_error)

        table_names = ['paymenttypes']
        permissions = check_user_permissions(user, table_names)
        payment_types = self.get_object()
        payment_types_data = self.get_serializer(payment_types).data
        return Response({'paymenttypes': payment_types_data, 'permissions': permissions})
