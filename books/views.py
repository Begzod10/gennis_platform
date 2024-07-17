from rest_framework import generics

from .models import Book, BookImage, CenterOrders, CenterBalance, BookOrder, CollectedBookPayments, BalanceOverhead
from .serializers import BookSerializer, BookImageSerializer, BookOrderSerializers, CenterOrdersSerializers, \
    CenterBalanceSerializers, BalanceOverheadSerializers, CollectedBookPaymentsSerializers


class BookOrderListCreateView(generics.ListCreateAPIView):
    queryset = BookOrder.objects.all()
    serializer_class = BookOrderSerializers


class BookOrderRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = BookOrder.objects.all()
    serializer_class = BookOrderSerializers


class BookListCreateView(generics.ListCreateAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer


class BookRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer


class BookImageListCreateView(generics.ListCreateAPIView):
    queryset = BookImage.objects.all()
    serializer_class = BookImageSerializer


class BookImageRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = BookImage.objects.all()
    serializer_class = BookImageSerializer
