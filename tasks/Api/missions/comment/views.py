from rest_framework import generics, permissions
from rest_framework import status
from rest_framework.response import Response
from tasks.models import MissionComment
from tasks.serializers import MissionCommentSerializer


class CommentListCreateAPIView(generics.ListCreateAPIView):
    queryset = MissionComment.objects.all()
    serializer_class = MissionCommentSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CommentDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = MissionComment.objects.all()
    serializer_class = MissionCommentSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"detail": "Deleted successfully"}, status=status.HTTP_200_OK)
