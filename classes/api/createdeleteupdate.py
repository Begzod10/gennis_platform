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

    def update(self, request, *args, **kwargs):
        from rest_framework.response import Response
        from ..serializers import ClassNumberListSerializers
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        class_types_data = validated_data.get('class_types', None)
        subjects_data = validated_data.get('subjects', None)
        instance = serializer.update(instance, validated_data)

        if class_types_data is not None:
            instance.class_types = class_types_data
        elif class_types_data is None and subjects_data is not None:
            instance.class_types = None

        if subjects_data is not None:
            instance.subjects.set(subjects_data)
        instance.save()
        instance.refresh_from_db()
        data = ClassNumberListSerializers(instance).data

        return Response(data)


class ClassNumberDestroyView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]

    queryset = ClassNumber.objects.all()
    serializer_class = ClassNumberSerializers
