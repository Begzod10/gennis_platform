from rest_framework import generics
from books.models import BookOrder, CollectedBookPayments, BalanceOverhead, CenterBalance, BookOverhead, BranchPayment, \
    EditorBalance, BookImage
from books.serializers import BookOrderListSerializers, BalanceOverheadListSerializers, \
    CollectedBookPaymentsListSerializers, BranchPaymentListSerializers, \
    CenterBalanceListSerializer, BookOverheadListSerializers, EditorBalanceListSerializers, BookImageListSerializer
from user.functions.functions import check_auth
from rest_framework.response import Response
from permissions.functions.CheckUserPermissions import check_user_permissions


# class BookImageListView(generics.ListAPIView):
#     queryset = BookImage.objects.all()
#     serializer_class = BookImageListSerializer
#
#     def get(self, request, *args, **kwargs):
#         user, auth_error = check_auth(request)
#         if auth_error:
#             return Response(auth_error)
#
#         table_names = ['bookimage', 'book']
#         permissions = check_user_permissions(user, table_names)
#
#         queryset = BookImage.objects.all()
#         serializer = BookImageListSerializer(queryset, many=True)
#         return Response({'bookimages': serializer.data, 'permissions': permissions})


class BookImageRetrieveView(generics.RetrieveAPIView):
    queryset = BookImage.objects.all()
    serializer_class = BookImageListSerializer

    def retrieve(self, request, *args, **kwargs):
        user, auth_error = check_auth(request)
        if auth_error:
            return Response(auth_error)

        table_names = ['bookimage', 'book']
        permissions = check_user_permissions(user, table_names)
        book_image = self.get_object()
        book_image_data = self.get_serializer(book_image).data
        return Response({'bookimage': book_image_data, 'permissions': permissions})


class EditorBalanceListView(generics.ListAPIView):
    queryset = EditorBalance.objects.all()
    serializer_class = EditorBalanceListSerializers

    def get(self, request, *args, **kwargs):
        user, auth_error = check_auth(request)
        if auth_error:
            return Response(auth_error)

        table_names = ['editorbalance', 'paymenttypes']
        permissions = check_user_permissions(user, table_names)

        queryset = EditorBalance.objects.all()
        serializer = EditorBalanceListSerializers(queryset, many=True)
        return Response({'editorbalances': serializer.data, 'permissions': permissions})


class EditorBalanceRetrieveView(generics.RetrieveAPIView):
    queryset = EditorBalance.objects.all()
    serializer_class = EditorBalanceListSerializers

    def retrieve(self, request, *args, **kwargs):
        user, auth_error = check_auth(request)
        if auth_error:
            return Response(auth_error)

        table_names = ['editorbalance', 'paymenttypes']
        permissions = check_user_permissions(user, table_names)
        editor_balance = self.get_object()
        editor_balance_data = self.get_serializer(editor_balance).data
        return Response({'editorbalance': editor_balance_data, 'permissions': permissions})


class BranchPaymentListView(generics.ListAPIView):
    queryset = BranchPayment.objects.all()
    serializer_class = BranchPaymentListSerializers

    def get(self, request, *args, **kwargs):
        user, auth_error = check_auth(request)
        if auth_error:
            return Response(auth_error)

        table_names = ['branchpayment', 'branch', 'bookorder', 'editorbalance', 'paymenttypes']
        permissions = check_user_permissions(user, table_names)

        queryset = BranchPayment.objects.all()
        serializer = BranchPaymentListSerializers(queryset, many=True)
        return Response({'branchpayments': serializer.data, 'permissions': permissions})


class BranchPaymentRetrieveView(generics.RetrieveAPIView):
    queryset = BranchPayment.objects.all()
    serializer_class = BranchPaymentListSerializers

    def retrieve(self, request, *args, **kwargs):
        user, auth_error = check_auth(request)
        if auth_error:
            return Response(auth_error)

        table_names = ['branchpayment', 'branch', 'bookorder', 'editorbalance', 'paymenttypes']
        permissions = check_user_permissions(user, table_names)
        branch_payment = self.get_object()
        branch_payment_data = self.get_serializer(branch_payment).data
        return Response({'branchpayment': branch_payment_data, 'permissions': permissions})


class BookOverheadListView(generics.ListAPIView):
    queryset = BookOverhead.objects.all()
    serializer_class = BookOverheadListSerializers

    def get(self, request, *args, **kwargs):
        user, auth_error = check_auth(request)
        if auth_error:
            return Response(auth_error)

        table_names = ['paymenttypes', 'bookoverhead', 'editorbalance']
        permissions = check_user_permissions(user, table_names)

        queryset = BookOrder.objects.all()
        serializer = BookOrderListSerializers(queryset, many=True)
        return Response({'bookoverheads': serializer.data, 'permissions': permissions})


class BookOverheadRetrieveView(generics.RetrieveAPIView):
    queryset = BookOverhead.objects.all()
    serializer_class = BookOverheadListSerializers

    def retrieve(self, request, *args, **kwargs):
        user, auth_error = check_auth(request)
        if auth_error:
            return Response(auth_error)

        table_names = ['paymenttypes', 'bookoverhead', 'editorbalance']
        permissions = check_user_permissions(user, table_names)
        book_overhead = self.get_object()
        book_overhead_data = self.get_serializer(book_overhead).data
        return Response({'bookoverhead': book_overhead_data, 'permissions': permissions})


class CenterBalanceListView(generics.ListAPIView):
    queryset = CenterBalance.objects.all()
    serializer_class = CenterBalanceListSerializer

    def get(self, request, *args, **kwargs):
        user, auth_error = check_auth(request)
        if auth_error:
            return Response(auth_error)

        table_names = ['centerbalance', 'branch']
        permissions = check_user_permissions(user, table_names)

        queryset = CenterBalance.objects.all()
        serializer = CenterBalanceListSerializer(queryset, many=True)
        return Response({'centerbalances': serializer.data, 'permissions': permissions})


class CenterBalanceRetrieveView(generics.RetrieveAPIView):
    queryset = CenterBalance.objects.all()
    serializer_class = CenterBalanceListSerializer

    def retrieve(self, request, *args, **kwargs):
        user, auth_error = check_auth(request)
        if auth_error:
            return Response(auth_error)

        table_names = ['centerbalance', 'branch']
        permissions = check_user_permissions(user, table_names)
        center_balance = self.get_object()
        center_balance_data = self.get_serializer(center_balance).data
        return Response({'centerbalance': center_balance_data, 'permissions': permissions})


class BalanceOverheadListView(generics.ListAPIView):
    queryset = BalanceOverhead.objects.all()
    serializer_class = BalanceOverheadListSerializers

    def get(self, request, *args, **kwargs):
        user, auth_error = check_auth(request)
        if auth_error:
            return Response(auth_error)

        table_names = ['balanceoverhead', 'centerbalance', 'branch', 'paymenttypes']
        permissions = check_user_permissions(user, table_names)

        queryset = BalanceOverhead.objects.all()
        serializer = BalanceOverheadListSerializers(queryset, many=True)
        return Response({'balanceoverheads': serializer.data, 'permissions': permissions})


class BalanceOverheadRetrieveView(generics.RetrieveAPIView):
    queryset = BalanceOverhead.objects.all()
    serializer_class = BalanceOverheadListSerializers

    def retrieve(self, request, *args, **kwargs):
        user, auth_error = check_auth(request)
        if auth_error:
            return Response(auth_error)

        table_names = ['balanceoverhead', 'centerbalance', 'branch', 'paymenttypes']
        permissions = check_user_permissions(user, table_names)
        balance_overhead = self.get_object()
        balance_overhead_data = self.get_serializer(balance_overhead).data
        return Response({'balanceoverhead': balance_overhead_data, 'permissions': permissions})


class CollectedBookPaymentsRetrieveView(generics.RetrieveAPIView):
    queryset = CollectedBookPayments.objects.all()
    serializer_class = CollectedBookPaymentsListSerializers

    def retrieve(self, request, *args, **kwargs):
        user, auth_error = check_auth(request)
        if auth_error:
            return Response(auth_error)

        table_names = ['collectedbookpayments', 'branch', 'paymenttypes']
        permissions = check_user_permissions(user, table_names)
        collected_book_payments = self.get_object()
        collected_book_payments_data = self.get_serializer(collected_book_payments).data
        return Response({'collectedbookpayments': collected_book_payments_data, 'permissions': permissions})


class BookOrderListView(generics.ListAPIView):
    queryset = BookOrder.objects.all()
    serializer_class = BookOrderListSerializers

    def get(self, request, *args, **kwargs):
        user, auth_error = check_auth(request)
        if auth_error:
            return Response(auth_error)

        table_names = ['bookorder', 'collectedbookpayments', 'customuser', 'student', 'teacher', 'book', 'group',
                       'branch']
        permissions = check_user_permissions(user, table_names)

        queryset = BookOrder.objects.all()
        serializer = BookOrderListSerializers(queryset, many=True)
        return Response({'bookorders': serializer.data, 'permissions': permissions})


class BookOrderRetrieveView(generics.RetrieveAPIView):
    queryset = BookOrder.objects.all()
    serializer_class = BookOrderListSerializers

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
