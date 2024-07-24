from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from ..serializers import FlowTypesSerializer
from ..models import FlowTypes


class FlowTypesListCreateView(generics.ListCreateAPIView):
    queryset = FlowTypes.objects.all()
    serializer_class = FlowTypesSerializer


class FlowTypesListView(generics.ListCreateAPIView):
    queryset = FlowTypes.objects.all()
    serializer_class = FlowTypesSerializer


class FlowTypesDelete(generics.RetrieveDestroyAPIView):
    queryset = FlowTypes.objects.all()
    serializer_class = FlowTypesSerializer
