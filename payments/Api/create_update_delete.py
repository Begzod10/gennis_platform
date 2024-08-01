from rest_framework import generics
from rest_framework.response import Response

from payments.models import PaymentTypes
from payments.serializers import (PaymentTypesSerializers)
from permissions.functions.CheckUserPermissions import check_user_permissions
from user.functions.functions import check_auth


class PaymentTypesCreate(generics.CreateAPIView):
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


class PaymentTypesUpdateAPIView(generics.UpdateAPIView):
    queryset = PaymentTypes.objects.all()
    serializer_class = PaymentTypesSerializers
