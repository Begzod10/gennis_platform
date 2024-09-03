import json

from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from books.models import BookOrder, CollectedBookPayments, BalanceOverhead, BookOverhead, BookImage, UserBook
from books.serializers import BookOrderSerializers, BalanceOverheadSerializers, CollectedBookPaymentsSerializers, \
    BookOverheadSerializers, BookImageSerializer, UserBookSerializer


class UserBookDestroyView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]

    queryset = UserBook.objects.all()
    serializer_class = UserBookSerializer


class BookImageCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]

    queryset = BookImage.objects.all()
    serializer_class = BookImageSerializer


class BookImageUpdateView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]

    queryset = BookImage.objects.all()
    serializer_class = BookImageSerializer


class BookImageDestroyView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]

    queryset = BookImage.objects.all()
    serializer_class = BookImageSerializer


class BookOverheadCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]

    queryset = BookOverhead.objects.all()
    serializer_class = BookOverheadSerializers


class BookOverheadUpdateView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]

    queryset = BookOverhead.objects.all()
    serializer_class = BookOverheadSerializers


class BookOverheadDestroyView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        data = json.loads(request.body)
        book_overhead = BookOverhead.objects.get(pk=pk)
        book_overhead.deleted_reason = data.get('deleted_reason')
        book_overhead.deleted = True
        serializer = BookOverheadSerializers(book_overhead)
        return Response({'data': serializer.data})


class BalanceOverheadCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]

    queryset = BalanceOverhead.objects.all()
    serializer_class = BalanceOverheadSerializers


class BalanceOverheadUpdateView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]

    queryset = BalanceOverhead.objects.all()
    serializer_class = BalanceOverheadSerializers


class BalanceOverheadDestroyView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]

    queryset = BalanceOverhead.objects.all()
    serializer_class = BalanceOverheadSerializers


class CollectedBookPaymentsUpdateView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]

    queryset = CollectedBookPayments.objects.all()
    serializer_class = CollectedBookPaymentsSerializers


class BookOrderCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]

    queryset = BookOrder.objects.all()
    serializer_class = BookOrderSerializers


class BookOrderUpdateView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]

    queryset = BookOrder.objects.all()
    serializer_class = BookOrderSerializers


class BookOrderDestroyView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]

    queryset = BookOrder.objects.all()
    serializer_class = BookOrderSerializers
