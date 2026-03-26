from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from tasks.models import MissionProof
from tasks.serializers import MissionProofSerializer, _sync_proof_to_management, _sync_proof_update_to_management, _sync_proof_delete_to_management
from django.conf import settings


class ProofListCreateAPIView(generics.ListCreateAPIView):
    queryset = MissionProof.objects.all()
    serializer_class = MissionProofSerializer

    def perform_create(self, serializer):
        instance = serializer.save()
        mgmt_id = _sync_proof_to_management(instance)
        if mgmt_id:
            instance.management_id = mgmt_id
            instance.save(update_fields=["management_id"])


class ProofDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = MissionProof.objects.all()
    serializer_class = MissionProofSerializer

    def perform_update(self, serializer):
        instance = serializer.save()
        if instance.management_id:
            _sync_proof_update_to_management(
                management_id=instance.management_id,
                file=instance.file.name if instance.file and instance.file.name and (instance.file.name.startswith("http://") or instance.file.name.startswith("https://")) else (f"{settings.BASE_URL}/media/{instance.file.name}" if instance.file else None),
                comment=instance.comment,
            )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        mgmt_id = instance.management_id
        self.perform_destroy(instance)
        if mgmt_id:
            _sync_proof_delete_to_management(mgmt_id)
        return Response({"detail": "Deleted successfully"}, status=status.HTTP_200_OK)
