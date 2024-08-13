from rest_framework import generics
from books.models import BookOrder, CollectedBookPayments, BalanceOverhead, BookOverhead, BookImage
from books.serializers import BookOrderSerializers, BalanceOverheadSerializers, CollectedBookPaymentsSerializers, \
    BookOverheadSerializers, BookImageSerializer
from rest_framework.response import Response
from rest_framework.views import APIView
import json


class BookImageCreateView(generics.CreateAPIView):
    queryset = BookImage.objects.all()
    serializer_class = BookImageSerializer


class BookImageUpdateView(generics.UpdateAPIView):
    queryset = BookImage.objects.all()
    serializer_class = BookImageSerializer


class BookImageDestroyView(generics.DestroyAPIView):
    queryset = BookImage.objects.all()
    serializer_class = BookImageSerializer


class BookOverheadCreateView(generics.CreateAPIView):
    queryset = BookOverhead.objects.all()
    serializer_class = BookOverheadSerializers


class BookOverheadUpdateView(generics.UpdateAPIView):
    queryset = BookOverhead.objects.all()
    serializer_class = BookOverheadSerializers


class BookOverheadDestroyView(APIView):
    def post(self, request, pk):
        data = json.loads(request.body)
        book_overhead = BookOverhead.objects.get(pk=pk)
        book_overhead.deleted_reason = data.get('deleted_reason')
        book_overhead.deleted = True
        serializer = BookOverheadSerializers(book_overhead)
        return Response({'data': serializer.data})


class BalanceOverheadCreateView(generics.CreateAPIView):
    queryset = BalanceOverhead.objects.all()
    serializer_class = BalanceOverheadSerializers


class BalanceOverheadUpdateView(generics.UpdateAPIView):
    queryset = BalanceOverhead.objects.all()
    serializer_class = BalanceOverheadSerializers


class BalanceOverheadDestroyView(generics.DestroyAPIView):
    queryset = BalanceOverhead.objects.all()
    serializer_class = BalanceOverheadSerializers


class CollectedBookPaymentsUpdateView(generics.UpdateAPIView):
    queryset = CollectedBookPayments.objects.all()
    serializer_class = CollectedBookPaymentsSerializers


class BookOrderCreateView(generics.CreateAPIView):
    queryset = BookOrder.objects.all()
    serializer_class = BookOrderSerializers


class BookOrderUpdateView(generics.UpdateAPIView):
    queryset = BookOrder.objects.all()
    serializer_class = BookOrderSerializers


class BookOrderDestroyView(generics.DestroyAPIView):
    queryset = BookOrder.objects.all()
    serializer_class = BookOrderSerializers
