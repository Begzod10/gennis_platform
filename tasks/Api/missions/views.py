from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from collections import OrderedDict
from django.utils.timezone import localdate
from rest_framework.response import Response
from tasks.filters import MissionFilter
from tasks.models import Mission
from tasks.serializers import MissionCrudSerializer, MissionDetailSerializer
from rest_framework import generics


class MissionListCreateAPIView(generics.ListCreateAPIView):
    queryset = Mission.objects.all().select_related(
        "creator", "executor", "reviewer", "branch", "redirected_by"
    ).prefetch_related("tags")
    filter_backends = [DjangoFilterBackend]
    filterset_class = MissionFilter

    def get_serializer_class(self):
        if self.request.method == "POST":
            return MissionCrudSerializer
        return MissionDetailSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        missions = serializer.save()  # LIST qaytadi

        read_serializer = MissionDetailSerializer(
            missions, many=True, context={"request": request}
        )
        return Response(read_serializer.data, status=status.HTTP_201_CREATED)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        creator = request.query_params.get("creator")
        executor = request.query_params.get("executor")
        reviewer = request.query_params.get("reviewer")

        serializer = MissionDetailSerializer(
            queryset, many=True, context={"request": request}
        )
        data = serializer.data

        # ⛔ executor yoki reviewer bo‘lsa — OLDINGIDEK
        if executor or reviewer or not creator:
            for item in data:
                item["is_grouped"] = False
            return Response(data)

        # ✅ CREATOR UCHUN GROUPING
        grouped = OrderedDict()

        for item in data:
            key = (
                item["title"],
                item["description"],
                item["category"],
                item["deadline"],
                item["creator"]["id"],
            )

            if key not in grouped:
                base = item.copy()
                base["is_grouped"] = True
                base["children"] = []
                grouped[key] = base

            grouped[key]["children"].append(item)

        return Response(list(grouped.values()))


class MissionDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Mission.objects.all().select_related("creator", "executor", "reviewer", "branch").prefetch_related(
        "tags", "subtasks", "attachments", "comments", "proofs")

    def get_serializer_class(self):
        if self.request.method in ["PUT", "PATCH", "DELETE"]:
            return MissionCrudSerializer
        return MissionDetailSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"detail": "Deleted successfully"}, status=status.HTTP_200_OK)
