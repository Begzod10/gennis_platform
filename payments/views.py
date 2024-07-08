from rest_framework import generics
from rest_framework.permissions import *

from gennis_platform.permission import IsAdminOrReadOnly

from .serializers import (PaymentTypesSerializers, PaymentTypes)



class CreatePaymentTypesList(generics.ListCreateAPIView):
    queryset = PaymentTypes.objects.all()
    serializer_class = PaymentTypesSerializers
    # permission_classes = (
    # IsAuthenticatedOrReadOnly, IsAdminOrReadOnly)  # login qilgan yoki yuq ligini va admin emasligini tekshiradi
    #


class PaymentTypesRetrieveUpdateAPIView(generics.RetrieveUpdateAPIView):
    queryset = PaymentTypes.objects.all()
    serializer_class = PaymentTypesSerializers
    # permission_classes = (
    # IsAuthenticatedOrReadOnly, IsAdminOrReadOnly)  # login qilgan yoki yuq ligini va admin emasligini tekshiradi
