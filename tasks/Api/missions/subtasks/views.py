from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from tasks.models import MissionSubtask
from tasks.serializers import MissionSubtaskSerializer, _sync_subtask_to_management, _sync_subtask_update_to_management, _sync_subtask_delete_to_management


class SubtaskListCreateAPIView(generics.ListCreateAPIView):
    queryset = MissionSubtask.objects.all()
    serializer_class = MissionSubtaskSerializer

    def perform_create(self, serializer):
        instance = serializer.save()
        mgmt_id = _sync_subtask_to_management(instance)
        if mgmt_id:
            instance.management_id = mgmt_id
            instance.save(update_fields=["management_id"])


class SubtaskDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = MissionSubtask.objects.all()
    serializer_class = MissionSubtaskSerializer

    def perform_update(self, serializer):
        instance = serializer.save()
        if instance.management_id:
            _sync_subtask_update_to_management(
                management_id=instance.management_id,
                title=instance.title,
                is_done=instance.is_done,
            )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        mgmt_id = instance.management_id
        self.perform_destroy(instance)
        if mgmt_id:
            _sync_subtask_delete_to_management(mgmt_id)
        return Response({"detail": "Deleted successfully"}, status=status.HTTP_200_OK)
