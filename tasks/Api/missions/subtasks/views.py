from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from tasks.models import MissionSubtask
from tasks.serializers import MissionSubtaskSerializer


class SubtaskListCreateAPIView(generics.ListCreateAPIView):
    queryset = MissionSubtask.objects.all()
    serializer_class = MissionSubtaskSerializer


class SubtaskDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = MissionSubtask.objects.all()
    serializer_class = MissionSubtaskSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"detail": "Deleted successfully"}, status=status.HTTP_200_OK)
