from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from classes.models import ClassNumber, ClassCoin, CoinInfo, StudentCoin
from classes.serializers import (ClassNumberSerializers,
                                 ClassCoinSerializers,
                                 StudentCoinSerializers, CoinInfoSerializers)
from permissions.response import CustomResponseMixin


class CoinInfoCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]

    queryset = CoinInfo.objects.all()
    serializer_class = CoinInfoSerializers


class CoinInfoUpdateView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]

    queryset = CoinInfo.objects.all()
    serializer_class = CoinInfoSerializers


class CoinInfoDestroyView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]

    queryset = CoinInfo.objects.all()
    serializer_class = CoinInfoSerializers


class StudentCoinCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]

    queryset = StudentCoin.objects.all()
    serializer_class = StudentCoinSerializers


class StudentCoinUpdateView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]

    queryset = StudentCoin.objects.all()
    serializer_class = StudentCoinSerializers


class StudentCoinDestroyView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]

    queryset = StudentCoin.objects.all()
    serializer_class = StudentCoinSerializers


class ClassCoinCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]

    queryset = ClassCoin.objects.all()
    serializer_class = ClassCoinSerializers


class ClassCoinUpdateView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]

    queryset = ClassCoin.objects.all()
    serializer_class = ClassCoinSerializers


class ClassCoinDestroyView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]

    queryset = ClassCoin.objects.all()
    serializer_class = ClassCoinSerializers


class ClassNumberCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]

    queryset = ClassNumber.objects.all()
    serializer_class = ClassNumberSerializers


class ClassNumberUpdateView(CustomResponseMixin, generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]

    queryset = ClassNumber.objects.all()
    serializer_class = ClassNumberSerializers


class ClassNumberDestroyView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]

    queryset = ClassNumber.objects.all()
    serializer_class = ClassNumberSerializers
