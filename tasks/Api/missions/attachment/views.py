from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from tasks.models import MissionAttachment
from tasks.serializers import MissionAttachmentSerializer


class AttachmentListCreateAPIView(generics.ListCreateAPIView):
    queryset = MissionAttachment.objects.all()
    serializer_class = MissionAttachmentSerializer


class AttachmentDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = MissionAttachment.objects.all()
    serializer_class = MissionAttachmentSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"detail": "Deleted successfully"}, status=status.HTTP_200_OK)
