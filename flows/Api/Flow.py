from rest_framework import generics
from rest_framework.response import Response

from ..serializers import FlowCreateUpdateSerializer, FlowsSerializer

from ..models import Flow


class FlowListCreateView(generics.ListCreateAPIView):
    queryset = Flow.objects.all()
    serializer_class = FlowCreateUpdateSerializer

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return FlowsSerializer
        return FlowCreateUpdateSerializer


class FlowListView(generics.ListAPIView):
    queryset = Flow.objects.all()
    serializer_class = FlowsSerializer


class FlowProfile(generics.RetrieveUpdateAPIView):
    queryset = Flow.objects.all()
    serializer_class = FlowCreateUpdateSerializer

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return FlowCreateUpdateSerializer
        return FlowsSerializer

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        instance.refresh_from_db()
        read_serializer = FlowsSerializer(instance)
        return Response(read_serializer.data)
