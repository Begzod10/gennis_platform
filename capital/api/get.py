from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from capital.functions.creat_capital_term import creat_capital_term
from capital.models import Capital, OldCapital
from capital.serializers import (CapitalListSerializers, OldCapitalListSerializers)
from permissions.response import QueryParamFilterMixin
from capital.serializer.old_capital import OldCapitalsListSerializersTotal
from django.db.models import Sum
from capital.filters import OldCapitalFilter
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from permissions.response import CustomPagination

class OldCapitalRetrieveAPIView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]

    queryset = OldCapital.objects.all()
    serializer_class = OldCapitalListSerializers

    def retrieve(self, request, *args, **kwargs):
        old_capital = self.get_object()
        old_capital_data = self.get_serializer(old_capital).data
        return Response(old_capital_data)


class OldCapitalListView(QueryParamFilterMixin, generics.ListAPIView):
    filter_mappings = {
        'branch': 'branch_id',
        'status': 'deleted',
    }
    permission_classes = [IsAuthenticated]

    queryset = OldCapital.objects.all()
    serializer_class = OldCapitalsListSerializersTotal
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = OldCapitalFilter

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        queryset = self.filter_queryset(queryset)

        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)

        data = [
            {
                "name": "Total Amount",
                "totalPayment": queryset.aggregate(total_sum=Sum('price'))['total_sum'] or 0,
                "totalPaymentCount": queryset.count(),
                "type": "amount"
            },
            {
                "name": "Cash Payments",
                "totalPayment":
                    queryset.filter(payment_type__name__iexact='Cash').aggregate(total_sum=Sum('price'))[
                        'total_sum'] or 0,
                "totalPaymentCount": queryset.filter(payment_type__name__iexact='Cash').count(),
                "type": "cash"
            },
            {
                "name": "Click Payments",
                "totalPayment":
                    queryset.filter(payment_type__name__iexact="Click").aggregate(total_sum=Sum('price'))[
                        'total_sum'] or 0,
                "totalPaymentCount": queryset.filter(payment_type__name__iexact="Click").count(),
                "type": "click"
            },
            {
                "name": "Bank Transfers",
                "totalPayment":
                    queryset.filter(payment_type__name__iexact="Bank").aggregate(total_sum=Sum('price'))[
                        'total_sum'] or 0,
                "totalPaymentCount": queryset.filter(payment_type__name__iexact="Bank").count(),
                "type": "bank"
            },
        ]

        return self.get_paginated_response({
            'data': serializer.data,
            'totalCount': data
        })

class CapitalRetrieveAPIView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]

    queryset = Capital.objects.all()
    serializer_class = CapitalListSerializers

    def retrieve(self, request, *args, **kwargs):
        capital = self.get_queryset()
        capital_data = self.get_serializer(capital, many=True).data
        return Response(capital_data)

    def get_queryset(self):
        user_id = self.kwargs.get('pk')
        capital = Capital.objects.filter(category_id=user_id).all()
        return capital


class CapitalRetrieveAPIViewOne(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]

    queryset = Capital.objects.all()
    serializer_class = CapitalListSerializers


class CapitalListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]

    queryset = Capital.objects.all()
    serializer_class = CapitalListSerializers

    def get(self, request, *args, **kwargs):

        queryset = Capital.objects.all()
        location_id = self.request.query_params.get('location_id', None)
        branch_id = self.request.query_params.get('branch_id', None)

        if branch_id is not None:
            queryset = queryset.filter(branch_id=branch_id)
        if location_id is not None:
            queryset = queryset.filter(location_id=location_id)
        serializer = CapitalListSerializers(queryset, many=True)
        for capital in serializer.data:
            creat_capital_term(capital)
        return Response(serializer.dat)
