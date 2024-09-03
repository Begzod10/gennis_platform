from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from branch.models import Branch
from branch.serializers import BranchSerializer
from permissions.response import CustomResponseMixin


class BranchCreateView(CustomResponseMixin, generics.CreateAPIView):
    permission_classes = [IsAuthenticated]

    queryset = Branch.objects.all()
    serializer_class = BranchSerializer


class BranchUpdateView(CustomResponseMixin, generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]

    queryset = Branch.objects.all()
    serializer_class = BranchSerializer


class BranchDestroyView(CustomResponseMixin, generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]

    queryset = Branch.objects.all()
    serializer_class = BranchSerializer

    def delete(self, request, *args, **kwargs):
        super().delete(request, *args, **kwargs)
        return Response({'message': 'deleted successfully'}, status=status.HTTP_200_OK)
