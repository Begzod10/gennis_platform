from rest_framework import generics
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from capital.models import Capital, OldCapital
from capital.serializers import (CapitalSerializers, OldCapitalSerializers)
from permissions.response import CustomResponseMixin


class OldCapitalCreateView(CustomResponseMixin, generics.CreateAPIView):
    permission_classes = [IsAuthenticated]

    queryset = OldCapital.objects.all()
    serializer_class = OldCapitalSerializers
    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        instance = OldCapital.objects.get(pk=response.data['id'])
        from capital.serializer.old_capital import OldCapitalsListSerializersTotal
        return Response(OldCapitalsListSerializersTotal(instance).data)


class OldCapitalUpdateView(CustomResponseMixin, generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]

    queryset = OldCapital.objects.all()
    serializer_class = OldCapitalSerializers
    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)

        instance = self.get_object()

        from capital.serializer.old_capital import OldCapitalsListSerializersTotal
        return Response(OldCapitalsListSerializersTotal(instance).data)


class OldCapitalDestroyView(CustomResponseMixin, generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]

    queryset = OldCapital.objects.all()
    serializer_class = OldCapitalSerializers

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()

        instance.deleted = True
        instance.save()
        return Response({"msg": "muvaffaqiyatlik o'chirildi"}, status=status.HTTP_200_OK)


class CapitalCreateView(CustomResponseMixin, generics.CreateAPIView):
    permission_classes = [IsAuthenticated]

    queryset = Capital.objects.all()
    serializer_class = CapitalSerializers


class CapitalUpdateView(CustomResponseMixin, generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]

    queryset = Capital.objects.all()
    serializer_class = CapitalSerializers


class CapitalDestroyView(CustomResponseMixin, generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]

    queryset = Capital.objects.all()
    serializer_class = CapitalSerializers
