from rest_framework import generics
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from gennis_platform.permission import IsAdminOrReadOnly
from .serializers import *


class StudentListCreateView(generics.ListCreateAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    # permission_classes = (
    #     IsAuthenticatedOrReadOnly, IsAdminOrReadOnly)  # login qilgan yoki yuq ligini va admin emasligini tekshiradi


class StudentRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    # permission_classes = (
    #     IsAuthenticatedOrReadOnly, IsAdminOrReadOnly)  # login qilgan yoki yuq ligini va admin emasligini tekshiradi
