from rest_framework import generics
from .serializers import (ClassTypesSerializers, ClassColorsSerializers, ClassNumberSerializers, ClassCoinSerializers,
                          StudentCoinSerializers, CoinInfoSerializers)
from .models import ClassNumber, ClassTypes, ClassColors, ClassCoin, CoinInfo, StudentCoin




class CreateClassCoinList(generics.ListCreateAPIView):
    queryset = ClassCoin.objects.all()
    serializer_class = ClassCoinSerializers


class ClassCoinRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ClassCoin.objects.all()
    serializer_class = ClassCoinSerializers


class CreateCoinInfoList(generics.ListCreateAPIView):
    queryset = CoinInfo.objects.all()
    serializer_class = CoinInfoSerializers


class CoinInfoRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CoinInfo.objects.all()
    serializer_class = CoinInfoSerializers


class CreateStudentCoinList(generics.ListCreateAPIView):
    queryset = StudentCoin.objects.all()
    serializer_class = StudentCoinSerializers


class StudentCoinRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = StudentCoin.objects.all()
    serializer_class = StudentCoinSerializers


class CreateClassNumberList(generics.ListCreateAPIView):
    queryset = ClassNumber.objects.all()
    serializer_class = ClassNumberSerializers


class ClassNumberRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ClassNumber.objects.all()
    serializer_class = ClassNumberSerializers


class CreateClassColorsList(generics.ListCreateAPIView):
    queryset = ClassColors.objects.all()
    serializer_class = ClassColorsSerializers


class ClassColorsRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ClassColors.objects.all()
    serializer_class = ClassColorsSerializers


class CreateClassTypesList(generics.ListCreateAPIView):
    queryset = ClassTypes.objects.all()
    serializer_class = ClassTypesSerializers


class ClassTypesRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ClassTypes.objects.all()
    serializer_class = ClassTypesSerializers
