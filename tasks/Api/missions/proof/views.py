from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from tasks.models import MissionProof
from tasks.serializers import MissionProofSerializer, _sync_proof_to_management


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

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"detail": "Deleted successfully"}, status=status.HTTP_200_OK)
