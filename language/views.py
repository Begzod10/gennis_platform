from rest_framework import generics
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from permissions.response import CustomResponseMixin
from .serializers import (Language, LanguageSerializers)


class CreateLanguageList(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]

    queryset = Language.objects.all()
    serializer_class = LanguageSerializers

    def get(self, request, *args, **kwargs):
        queryset = Language.objects.all()
        serializer = LanguageSerializers(queryset, many=True)
        return Response(serializer.data)


class LanguageRetrieveUpdateDestroyAPIView(CustomResponseMixin, generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]

    queryset = Language.objects.all()
    serializer_class = LanguageSerializers  # permission_classes = (IsAuthenticatedOrReadOnly, IsAdminOrReadOnly) # login qilgan yoki yuq ligini va admin emasligini tekshiradi

    def retrieve(self, request, *args, **kwargs):
        language = self.get_object()
        language_data = self.get_serializer(language).data
        return Response(language_data)

    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        return Response({'deleted': "True"}, status=status.HTTP_200_OK)
