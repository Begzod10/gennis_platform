from rest_framework import generics, permissions
from rest_framework import status
from rest_framework.response import Response
from tasks.models import MissionComment
from tasks.serializers import MissionCommentSerializer, _sync_comment_to_management, _sync_comment_update_to_management, _sync_comment_delete_to_management
from django.conf import settings


class CommentListCreateAPIView(generics.ListCreateAPIView):
    queryset = MissionComment.objects.all()
    serializer_class = MissionCommentSerializer

    def perform_create(self, serializer):
        instance = serializer.save()
        mgmt_id = _sync_comment_to_management(instance)
        if mgmt_id:
            instance.management_id = mgmt_id
            instance.save(update_fields=["management_id"])


class CommentDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = MissionComment.objects.all()
    serializer_class = MissionCommentSerializer

    def perform_update(self, serializer):
        instance = serializer.save()
        if instance.management_id:
            _sync_comment_update_to_management(
                management_id=instance.management_id,
                text=instance.text,
                attachment=f"{settings.BASE_URL}/media/{instance.attachment.name}" if instance.attachment else None,
            )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        mgmt_id = instance.management_id
        self.perform_destroy(instance)
        if mgmt_id:
            _sync_comment_delete_to_management(mgmt_id)
        return Response({"detail": "Deleted successfully"}, status=status.HTTP_200_OK)
