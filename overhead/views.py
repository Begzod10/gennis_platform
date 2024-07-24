from rest_framework import generics
from .models import Overhead
from .serializers import OverheadSerializer


class OverheadListCreateView(generics.ListCreateAPIView):
    queryset = Overhead.objects.all()
    serializer_class = OverheadSerializer


class OverheadRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Overhead.objects.all()
    serializer_class = OverheadSerializer
