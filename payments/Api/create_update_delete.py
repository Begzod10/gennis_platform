from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from payments.models import PaymentTypes
from payments.serializers import (PaymentTypesSerializers)


class PaymentTypesCreate(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]

    queryset = PaymentTypes.objects.all()
    serializer_class = PaymentTypesSerializers

    def get(self, request, *args, **kwargs):
        queryset = PaymentTypes.objects.all()
        serializer = PaymentTypesSerializers(queryset, many=True)
        return Response(serializer.data)


class PaymentTypesUpdateAPIView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]

    queryset = PaymentTypes.objects.all()
    serializer_class = PaymentTypesSerializers
