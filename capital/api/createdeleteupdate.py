from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response

from capital.models import Capital, OldCapital
from capital.serializers import (CapitalSerializers, OldCapitalSerializers)


class OldCapitalCreateView(generics.CreateAPIView):
    queryset = OldCapital.objects.all()
    serializer_class = OldCapitalSerializers


class OldCapitalUpdateView(generics.UpdateAPIView):
    queryset = OldCapital.objects.all()
    serializer_class = OldCapitalSerializers


class OldCapitalDestroyView(generics.DestroyAPIView):
    queryset = OldCapital.objects.all()
    serializer_class = OldCapitalSerializers

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()

        instance.deleted = True
        instance.save()
        return Response({"msg": "muvaffaqiyatlik o'chirildi"}, status=status.HTTP_200_OK)


class CapitalCreateView(generics.CreateAPIView):
    queryset = Capital.objects.all()
    serializer_class = CapitalSerializers


class CapitalUpdateView(generics.UpdateAPIView):
    queryset = Capital.objects.all()
    serializer_class = CapitalSerializers


class CapitalDestroyView(generics.DestroyAPIView):
    queryset = Capital.objects.all()
    serializer_class = CapitalSerializers
