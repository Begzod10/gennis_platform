from rest_framework import generics

from overhead.models import Overhead
from overhead.serializers import OverheadSerializerCreate


class OverheadCreateView(generics.CreateAPIView):
    queryset = Overhead.objects.all()
    serializer_class = OverheadSerializerCreate


class OverheadUpdateView(generics.UpdateAPIView):
    queryset = Overhead.objects.all()
    serializer_class = OverheadSerializerCreate


class OverheadDestroyView(generics.DestroyAPIView):
    queryset = Overhead.objects.all()
    serializer_class = OverheadSerializerCreate
