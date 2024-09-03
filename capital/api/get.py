from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from capital.functions.creat_capital_term import creat_capital_term
from capital.models import Capital, OldCapital
from capital.serializers import (CapitalListSerializers, OldCapitalListSerializers)


class OldCapitalRetrieveAPIView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]

    queryset = OldCapital.objects.all()
    serializer_class = OldCapitalListSerializers

    def retrieve(self, request, *args, **kwargs):
        old_capital = self.get_object()
        old_capital_data = self.get_serializer(old_capital).data
        return Response(old_capital_data)


class OldCapitalListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]

    queryset = OldCapital.objects.all()
    serializer_class = OldCapitalListSerializers

    def get(self, request, *args, **kwargs):

        queryset = OldCapital.objects.all()
        location_id = self.request.query_params.get('location_id', None)
        branch_id = self.request.query_params.get('branch_id', None)
        status = self.request.query_params.get('status', None)

        if branch_id is not None:
            queryset = queryset.filter(branch_id=branch_id)
        if location_id is not None:
            queryset = queryset.filter(location_id=location_id)
        if status is not None:
            queryset = queryset.filter(deleted=status)
        serializer = OldCapitalListSerializers(queryset, many=True)
        return Response(serializer.data)


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
