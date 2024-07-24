from rest_framework import generics
from capital.serializers import (CapitalSerializers)
from capital.models import Capital


class CapitalCreateView(generics.CreateAPIView):
    queryset = Capital.objects.all()
    serializer_class = CapitalSerializers


class CapitalUpdateView(generics.UpdateAPIView):
    queryset = Capital.objects.all()
    serializer_class = CapitalSerializers


class CapitalDestroyView(generics.DestroyAPIView):
    queryset = Capital.objects.all()
    serializer_class = CapitalSerializers
