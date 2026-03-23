from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from tasks.models import MissionAttachment
from tasks.serializers import MissionAttachmentSerializer, _sync_attachment_to_management


class AttachmentListCreateAPIView(generics.ListCreateAPIView):
    queryset = MissionAttachment.objects.all()
    serializer_class = MissionAttachmentSerializer

    def perform_create(self, serializer):
        instance = serializer.save()
        mgmt_id = _sync_attachment_to_management(instance)
        if mgmt_id:
            instance.management_id = mgmt_id
            instance.save(update_fields=["management_id"])


class AttachmentDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = MissionAttachment.objects.all()
    serializer_class = MissionAttachmentSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"detail": "Deleted successfully"}, status=status.HTTP_200_OK)
