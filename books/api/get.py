from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from books.models import BookOrder, CollectedBookPayments, BalanceOverhead, CenterBalance, BookOverhead, BranchPayment, \
    EditorBalance, BookImage, UserBook
from books.serializers import BookOrderListSerializers, BalanceOverheadListSerializers, \
    CollectedBookPaymentsListSerializers, BranchPaymentListSerializers, \
    CenterBalanceListSerializer, BookOverheadListSerializers, EditorBalanceListSerializers, BookImageListSerializer, \
    UserBookListSerializer
from permissions.response import QueryParamFilterMixin


class UserBookListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]

    queryset = UserBook.objects.all()
    serializer_class = UserBookListSerializer

    def get(self, request, *args, **kwargs):

        queryset = UserBook.objects.all()
        location_id = self.request.query_params.get('location_id', None)
        branch_id = self.request.query_params.get('branch_id', None)

        if branch_id is not None:
            queryset = queryset.filter(branch_id=branch_id)
        if location_id is not None:
            queryset = queryset.filter(location_id=location_id)
        serializer = UserBookListSerializer(queryset, many=True)
        return Response(serializer.data)


class UserBookRetrieveView(generics.RetrieveAPIView):
    queryset = UserBook.objects.all()
    serializer_class = UserBookListSerializer
    permission_classes = [IsAuthenticated]

    def retrieve(self, request, *args, **kwargs):
        user_book = self.get_object()
        user_book_data = self.get_serializer(user_book).data
        return Response(user_book_data)


class BookImageRetrieveView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]

    queryset = BookImage.objects.all()
    serializer_class = BookImageListSerializer

    def retrieve(self, request, *args, **kwargs):
        book_image = self.get_object()
        book_image_data = self.get_serializer(book_image).data
        return Response(book_image_data)


class EditorBalanceListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]

    queryset = EditorBalance.objects.all()
    serializer_class = EditorBalanceListSerializers

    def get(self, request, *args, **kwargs):

        queryset = EditorBalance.objects.all()
        location_id = self.request.query_params.get('location_id', None)
        branch_id = self.request.query_params.get('branch_id', None)

        if branch_id is not None:
            queryset = queryset.filter(branch_id=branch_id)
        if location_id is not None:
            queryset = queryset.filter(location_id=location_id)
        serializer = EditorBalanceListSerializers(queryset, many=True)
        return Response(serializer.data)


class EditorBalanceRetrieveView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]

    queryset = EditorBalance.objects.all()
    serializer_class = EditorBalanceListSerializers

    def retrieve(self, request, *args, **kwargs):
        editor_balance = self.get_object()
        editor_balance_data = self.get_serializer(editor_balance).data
        return Response(editor_balance_data)


class BranchPaymentListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]

    queryset = BranchPayment.objects.all()
    serializer_class = BranchPaymentListSerializers

    def get(self, request, *args, **kwargs):

        queryset = BranchPayment.objects.all()
        location_id = self.request.query_params.get('location_id', None)
        branch_id = self.request.query_params.get('branch_id', None)

        if branch_id is not None:
            queryset = queryset.filter(branch_id=branch_id)
        if location_id is not None:
            queryset = queryset.filter(location_id=location_id)
        serializer = BranchPaymentListSerializers(queryset, many=True)
        return Response(serializer.data)


class BranchPaymentRetrieveView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]

    queryset = BranchPayment.objects.all()
    serializer_class = BranchPaymentListSerializers

    def retrieve(self, request, *args, **kwargs):
        branch_payment = self.get_object()
        branch_payment_data = self.get_serializer(branch_payment).data
        return Response(branch_payment_data)


class BookOverheadListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]

    queryset = BookOverhead.objects.all()
    serializer_class = BookOverheadListSerializers

    def get(self, request, *args, **kwargs):

        queryset = BookOrder.objects.all()
        location_id = self.request.query_params.get('location_id', None)
        branch_id = self.request.query_params.get('branch_id', None)

        if branch_id is not None:
            queryset = queryset.filter(branch_id=branch_id)
        if location_id is not None:
            queryset = queryset.filter(location_id=location_id)
        serializer = BookOrderListSerializers(queryset, many=True)
        return Response(serializer.data)


class BookOverheadRetrieveView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]

    queryset = BookOverhead.objects.all()
    serializer_class = BookOverheadListSerializers

    def retrieve(self, request, *args, **kwargs):
        book_overhead = self.get_object()
        book_overhead_data = self.get_serializer(book_overhead).data
        return Response(book_overhead_data)


class CenterBalanceListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]

    queryset = CenterBalance.objects.all()
    serializer_class = CenterBalanceListSerializer

    def get(self, request, *args, **kwargs):

        queryset = CenterBalance.objects.all()
        location_id = self.request.query_params.get('location_id', None)
        branch_id = self.request.query_params.get('branch_id', None)

        if branch_id is not None:
            queryset = queryset.filter(branch_id=branch_id)
        if location_id is not None:
            queryset = queryset.filter(location_id=location_id)
        serializer = CenterBalanceListSerializer(queryset, many=True)
        return Response(serializer.data)


class CenterBalanceRetrieveView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]

    queryset = CenterBalance.objects.all()
    serializer_class = CenterBalanceListSerializer

    def retrieve(self, request, *args, **kwargs):
        center_balance = self.get_object()
        center_balance_data = self.get_serializer(center_balance).data
        return Response(center_balance_data)


class BalanceOverheadListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]

    queryset = BalanceOverhead.objects.all()
    serializer_class = BalanceOverheadListSerializers

    def get(self, request, *args, **kwargs):

        queryset = BalanceOverhead.objects.all()
        location_id = self.request.query_params.get('location_id', None)
        branch_id = self.request.query_params.get('branch_id', None)

        if branch_id is not None:
            queryset = queryset.filter(branch_id=branch_id)
        if location_id is not None:
            queryset = queryset.filter(location_id=location_id)
        serializer = BalanceOverheadListSerializers(queryset, many=True)
        return Response(serializer.data)


class BalanceOverheadRetrieveView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]

    queryset = BalanceOverhead.objects.all()
    serializer_class = BalanceOverheadListSerializers

    def retrieve(self, request, *args, **kwargs):
        balance_overhead = self.get_object()
        balance_overhead_data = self.get_serializer(balance_overhead).data
        return Response(balance_overhead_data)


class CollectedBookPaymentsRetrieveView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]

    queryset = CollectedBookPayments.objects.all()
    serializer_class = CollectedBookPaymentsListSerializers

    def retrieve(self, request, *args, **kwargs):
        collected_book_payments = self.get_object()
        collected_book_payments_data = self.get_serializer(collected_book_payments).data
        return Response(collected_book_payments_data)


class BookOrderListView(generics.ListAPIView, QueryParamFilterMixin):
    permission_classes = [IsAuthenticated]

    queryset = BookOrder.objects.all()
    serializer_class = BookOrderListSerializers
    filter_mappings = {
        'branch_id': 'branch',
        'student_id': 'student',
    }

    def get(self, request, *args, **kwargs):
        queryset = BookOrder.objects.all()

        queryset = self.filter_queryset(queryset)
        serializer = BookOrderListSerializers(queryset, many=True)
        return Response(serializer.data)


class BookOrderRetrieveView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]

    queryset = BookOrder.objects.all()
    serializer_class = BookOrderListSerializers

    def retrieve(self, request, *args, **kwargs):
        book_order = self.get_object()
        book_order_data = self.get_serializer(book_order).data
        return Response(book_order_data)
