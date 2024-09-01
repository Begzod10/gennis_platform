from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import ClassTypes, ClassColors
from .serializers import (ClassTypesSerializers, ClassColorsSerializers)


class CreateClassColorsList(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]

    queryset = ClassColors.objects.all()
    serializer_class = ClassColorsSerializers

    def get(self, request, *args, **kwargs):
        queryset = ClassColors.objects.all()
        serializer = ClassColorsSerializers(queryset, many=True)
        return Response(serializer.data)


class ClassColorsRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]

    queryset = ClassColors.objects.all()
    serializer_class = ClassColorsSerializers

    def retrieve(self, request, *args, **kwargs):
        class_colors = self.get_object()
        class_colors_data = self.get_serializer(class_colors).data
        return Response(class_colors_data)


class CreateClassTypesList(generics.ListCreateAPIView):
    queryset = ClassTypes.objects.all()
    serializer_class = ClassTypesSerializers

    def get(self, request, *args, **kwargs):
        queryset = ClassTypes.objects.all()
        serializer = ClassTypesSerializers(queryset, many=True)
        return Response(serializer.data)


class ClassTypesRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]

    queryset = ClassTypes.objects.all()
    serializer_class = ClassTypesSerializers

    def retrieve(self, request, *args, **kwargs):
        class_types = self.get_object()
        class_types_data = self.get_serializer(class_types).data
        return Response(class_types_data)
