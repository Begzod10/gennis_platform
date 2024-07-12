from rest_framework import generics
from .serializers import (ClassTypesSerializers, ClassColorsSerializers, ClassNumberSerializers)
from .models import ClassNumber, ClassTypes, ClassColors


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
