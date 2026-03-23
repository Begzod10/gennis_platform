from rest_framework import generics, permissions
from rest_framework import status
from rest_framework.response import Response
from tasks.models import MissionComment
from tasks.serializers import MissionCommentSerializer, _sync_comment_to_management


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

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"detail": "Deleted successfully"}, status=status.HTTP_200_OK)
