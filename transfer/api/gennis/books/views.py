from rest_framework import generics
from .serializers import TransferCollectedBookPaymentsSerializer, TransferBookOrderSerializer, \
    TransferCenterBalanceSerializer, TransferBalanceOverheadSerializer, TransferEditorBalanceSerializer, \
    TransferBranchPaymentSerializer, TransferUserBookSerializer
from books.models import CollectedBookPayments, BookOrder, CenterBalance, BalanceOverhead, EditorBalance, BranchPayment, \
    UserBook


class TransferUserBookCreateView(generics.CreateAPIView):
    queryset = UserBook.objects.all()
    serializer_class = TransferUserBookSerializer


class TransferBranchPaymentCreateView(generics.CreateAPIView):
    queryset = BranchPayment.objects.all()
    serializer_class = TransferBranchPaymentSerializer


class TransferEditorBalanceCreateView(generics.CreateAPIView):
    queryset = EditorBalance.objects.all()
    serializer_class = TransferEditorBalanceSerializer


class TransferBalanceOverheadCreateView(generics.CreateAPIView):
    queryset = BalanceOverhead.objects.all()
    serializer_class = TransferBalanceOverheadSerializer


class TransferCenterBalanceCreateView(generics.CreateAPIView):
    queryset = CenterBalance.objects.all()
    serializer_class = TransferCenterBalanceSerializer


class TransferBookOrderCreateView(generics.CreateAPIView):
    queryset = BookOrder.objects.all()
    serializer_class = TransferBookOrderSerializer


class TransferCollectedBookPaymentsCreateView(generics.CreateAPIView):
    queryset = CollectedBookPayments.objects.all()
    serializer_class = TransferCollectedBookPaymentsSerializer
