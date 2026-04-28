from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from payments.models import PaymentTypes
from payments.serializers import (PaymentTypesSerializers)


class PaymentTypesList(generics.ListAPIView):
    permission_classes = [IsAuthenticated]

    queryset = PaymentTypes.objects.all()
    serializer_class = PaymentTypesSerializers

    def get(self, request, *args, **kwargs):
        queryset = PaymentTypes.objects.all()
        serializer = PaymentTypesSerializers(queryset, many=True)
        return Response(serializer.data)


class PaymentTypesRetrieveAPIView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]

    queryset = PaymentTypes.objects.all()
    serializer_class = PaymentTypesSerializers

    def retrieve(self, request, *args, **kwargs):
        payment_types = self.get_object()
        payment_types_data = self.get_serializer(payment_types).data
        return Response(payment_types_data)
