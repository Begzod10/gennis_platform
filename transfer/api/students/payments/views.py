from rest_framework import generics

from students.models import StudentPayment
from transfer.api.students.payments.serializers import StudentPaymentSerializerTransfer


class StudentPaymentCreateView(generics.CreateAPIView):
    queryset = StudentPayment.objects.all()
    serializer_class = StudentPaymentSerializerTransfer
