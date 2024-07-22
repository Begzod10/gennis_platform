from rest_framework import generics
from .models import Book, BookImage, BookOrder, CollectedBookPayments, BalanceOverhead
from .serializers import BookSerializer, BookImageSerializer, BookOrderSerializers, \
    BalanceOverheadSerializers, CollectedBookPaymentsSerializers
from user.functions.functions import check_auth
from rest_framework.response import Response
from permissions.functions.CheckUserPermissions import check_user_permissions


class BalanceOverheadListCreateView(generics.ListCreateAPIView):
    queryset = BalanceOverhead.objects.all()
    serializer_class = BalanceOverheadSerializers

    def get(self, request, *args, **kwargs):
        user, auth_error = check_auth(request)
        if auth_error:
            return Response(auth_error)

        table_names = ['balanceoverhead', 'centerbalance', 'branch', 'paymenttypes']
        permissions = check_user_permissions(user, table_names)

        queryset = BalanceOverhead.objects.all()
        serializer = BalanceOverheadSerializers(queryset, many=True)
        return Response({'balanceoverheads': serializer.data, 'permissions': permissions})


class BalanceOverheadRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = BalanceOverhead.objects.all()
    serializer_class = BalanceOverheadSerializers

    def retrieve(self, request, *args, **kwargs):
        user, auth_error = check_auth(request)
        if auth_error:
            return Response(auth_error)

        table_names = ['balanceoverhead', 'centerbalance', 'branch', 'paymenttypes']
        permissions = check_user_permissions(user, table_names)
        balance_overhead = self.get_object()
        balance_overhead_data = self.get_serializer(balance_overhead).data
        return Response({'balanceoverhead': balance_overhead_data, 'permissions': permissions})


class CollectedBookPaymentsRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CollectedBookPayments.objects.all()
    serializer_class = CollectedBookPaymentsSerializers

    def retrieve(self, request, *args, **kwargs):
        user, auth_error = check_auth(request)
        if auth_error:
            return Response(auth_error)

        table_names = ['collectedbookpayments', 'branch', 'paymenttypes']
        permissions = check_user_permissions(user, table_names)
        collected_book_payments = self.get_object()
        collected_book_payments_data = self.get_serializer(collected_book_payments).data
        return Response({'collectedbookpayments': collected_book_payments_data, 'permissions': permissions})


class BookOrderListCreateView(generics.ListCreateAPIView):
    queryset = BookOrder.objects.all()
    serializer_class = BookOrderSerializers

    def get(self, request, *args, **kwargs):
        user, auth_error = check_auth(request)
        if auth_error:
            return Response(auth_error)

        table_names = ['bookorder', 'collectedbookpayments', 'customuser', 'student', 'teacher', 'book', 'group',
                       'branch']
        permissions = check_user_permissions(user, table_names)

        queryset = BookOrder.objects.all()
        serializer = BookOrderSerializers(queryset, many=True)
        return Response({'bookorders': serializer.data, 'permissions': permissions})


class BookOrderRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = BookOrder.objects.all()
    serializer_class = BookOrderSerializers

    def retrieve(self, request, *args, **kwargs):
        user, auth_error = check_auth(request)
        if auth_error:
            return Response(auth_error)

        table_names = ['bookorder', 'collectedbookpayments', 'customuser', 'student', 'teacher', 'book', 'group',
                       'branch']
        permissions = check_user_permissions(user, table_names)
        book_order = self.get_object()
        book_order_data = self.get_serializer(book_order).data
        return Response({'bookorder': book_order_data, 'permissions': permissions})


class BookListCreateView(generics.ListCreateAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer

    def get(self, request, *args, **kwargs):
        user, auth_error = check_auth(request)
        if auth_error:
            return Response(auth_error)

        table_names = ['book']
        permissions = check_user_permissions(user, table_names)

        queryset = Book.objects.all()
        serializer = BookSerializer(queryset, many=True)
        return Response({'books': serializer.data, 'permissions': permissions})


class BookRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer

    def retrieve(self, request, *args, **kwargs):
        user, auth_error = check_auth(request)
        if auth_error:
            return Response(auth_error)

        table_names = ['book']
        permissions = check_user_permissions(user, table_names)
        book = self.get_object()
        book_data = self.get_serializer(book).data
        return Response({'book': book_data, 'permissions': permissions})


class BookImageListCreateView(generics.ListCreateAPIView):
    queryset = BookImage.objects.all()
    serializer_class = BookImageSerializer

    def get(self, request, *args, **kwargs):
        user, auth_error = check_auth(request)
        if auth_error:
            return Response(auth_error)

        table_names = ['bookimage', 'book']
        permissions = check_user_permissions(user, table_names)

        queryset = BookImage.objects.all()
        serializer = BookImageSerializer(queryset, many=True)
        return Response({'bookimages': serializer.data, 'permissions': permissions})


class BookImageRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = BookImage.objects.all()
    serializer_class = BookImageSerializer

    def retrieve(self, request, *args, **kwargs):
        user, auth_error = check_auth(request)
        if auth_error:
            return Response(auth_error)

        table_names = ['bookimage', 'book']
        permissions = check_user_permissions(user, table_names)
        book_image = self.get_object()
        book_image_data = self.get_serializer(book_image).data
        return Response({'bookimage': book_image_data, 'permissions': permissions})
