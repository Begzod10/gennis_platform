from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Party, PartyTask
from .serializers import PartySerializer, PartyTaskSerializer


class PartyViewSet(viewsets.ModelViewSet):
    queryset = Party.objects.all()
    serializer_class = PartySerializer

    @action(detail=False, methods=["get"], url_path="select-options")
    def select_options(self, request):
        data = Party.objects.values("id", "name")
        formatted = [
            {"label": item["name"], "value": item["id"]}
            for item in data
        ]
        return Response(formatted)
class PartyTaskViewSet(viewsets.ModelViewSet):
    queryset = PartyTask.objects.all().prefetch_related("parties")
    serializer_class = PartyTaskSerializer