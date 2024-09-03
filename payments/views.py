from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import PaymentTypes
from .serializers import (PaymentTypesSerializers)


class CreatePaymentTypesList(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]

    queryset = PaymentTypes.objects.all()
    serializer_class = PaymentTypesSerializers

    def get(self, request, *args, **kwargs):
        queryset = PaymentTypes.objects.all()
        serializer = PaymentTypesSerializers(queryset, many=True)
        return Response(serializer.data)


class PaymentTypesRetrieveUpdateAPIView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]

    queryset = PaymentTypes.objects.all()
    serializer_class = PaymentTypesSerializers

    def retrieve(self, request, *args, **kwargs):
        payment_types = self.get_object()
        payment_types_data = self.get_serializer(payment_types).data
        return Response(payment_types_data)
