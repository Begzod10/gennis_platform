from django_filters.rest_framework import DjangoFilterBackend
from tasks.filters import MissionFilter
from tasks.models import Mission
from tasks.serializers import MissionCrudSerializer, MissionDetailSerializer
from rest_framework import generics


class MissionListCreateAPIView(generics.ListCreateAPIView):
    queryset = Mission.objects.all().select_related("creator", "executor", "reviewer", "branch").prefetch_related(
        "tags")
    filter_backends = [DjangoFilterBackend]
    filterset_class = MissionFilter

    def get_serializer_class(self):
        if self.request.method == "POST":
            return MissionCrudSerializer
        return MissionDetailSerializer

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)


class MissionDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Mission.objects.all().select_related("creator", "executor", "reviewer", "branch").prefetch_related(
        "tags", "subtasks", "attachments", "comments", "proofs")

    def get_serializer_class(self):
        if self.request.method in ["PUT", "PATCH", "DELETE"]:
            return MissionCrudSerializer
        return MissionDetailSerializer
