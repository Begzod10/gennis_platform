from rest_framework import generics
from classes.serializers import (ClassNumberSerializers,
                                 ClassCoinSerializers,
                                 StudentCoinSerializers, CoinInfoSerializers)
from classes.models import ClassNumber, ClassCoin, CoinInfo, StudentCoin


class CoinInfoCreateView(generics.CreateAPIView):
    queryset = CoinInfo.objects.all()
    serializer_class = CoinInfoSerializers


class CoinInfoUpdateView(generics.UpdateAPIView):
    queryset = CoinInfo.objects.all()
    serializer_class = CoinInfoSerializers


class CoinInfoDestroyView(generics.DestroyAPIView):
    queryset = CoinInfo.objects.all()
    serializer_class = CoinInfoSerializers


class StudentCoinCreateView(generics.CreateAPIView):
    queryset = StudentCoin.objects.all()
    serializer_class = StudentCoinSerializers


class StudentCoinUpdateView(generics.UpdateAPIView):
    queryset = StudentCoin.objects.all()
    serializer_class = StudentCoinSerializers


class StudentCoinDestroyView(generics.DestroyAPIView):
    queryset = StudentCoin.objects.all()
    serializer_class = StudentCoinSerializers


class ClassCoinCreateView(generics.CreateAPIView):
    queryset = ClassCoin.objects.all()
    serializer_class = ClassCoinSerializers


class ClassCoinUpdateView(generics.UpdateAPIView):
    queryset = ClassCoin.objects.all()
    serializer_class = ClassCoinSerializers


class ClassCoinDestroyView(generics.DestroyAPIView):
    queryset = ClassCoin.objects.all()
    serializer_class = ClassCoinSerializers


class ClassNumberCreateView(generics.CreateAPIView):
    queryset = ClassNumber.objects.all()
    serializer_class = ClassNumberSerializers


class ClassNumberUpdateView(generics.UpdateAPIView):
    queryset = ClassNumber.objects.all()
    serializer_class = ClassNumberSerializers


class ClassNumberDestroyView(generics.DestroyAPIView):
    queryset = ClassNumber.objects.all()
    serializer_class = ClassNumberSerializers
