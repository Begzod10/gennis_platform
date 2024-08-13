from rest_framework import generics
from capital.serializers import (CapitalSerializers, OldCapitalSerializers)
from capital.models import Capital, OldCapital


class OldCapitalCreateView(generics.CreateAPIView):
    queryset = OldCapital.objects.all()
    serializer_class = OldCapitalSerializers


class OldCapitalUpdateView(generics.UpdateAPIView):
    queryset = OldCapital.objects.all()
    serializer_class = OldCapitalSerializers


class OldCapitalDestroyView(generics.DestroyAPIView):
    queryset = OldCapital.objects.all()
    serializer_class = OldCapitalSerializers


class CapitalCreateView(generics.CreateAPIView):
    queryset = Capital.objects.all()
    serializer_class = CapitalSerializers


class CapitalUpdateView(generics.UpdateAPIView):
    queryset = Capital.objects.all()
    serializer_class = CapitalSerializers


class CapitalDestroyView(generics.DestroyAPIView):
    queryset = Capital.objects.all()
    serializer_class = CapitalSerializers
