from rest_framework import generics
from rest_framework.permissions import *

from gennis_patform.permission import IsAdminOrReadOnly
from .serializers import *


class CreateLanguageList(generics.ListCreateAPIView):
    queryset = Language.objects.all()
    serializer_class = LanguageSerializers
    permission_classes = (IsAuthenticatedOrReadOnly, IsAdminOrReadOnly) # login qilgan yoki yuq ligini va admin emasligini tekshiradi


class LanguageRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Language.objects.all()
    serializer_class = LanguageSerializers
    permission_classes = (IsAuthenticatedOrReadOnly, IsAdminOrReadOnly) # login qilgan yoki yuq ligini va admin emasligini tekshiradi
