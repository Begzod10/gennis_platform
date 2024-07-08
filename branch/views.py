from rest_framework import generics
from gennis_platform.permission import IsAdminOrReadOnly
from .serializers import (BranchSerializer, Branch)


class CreateBranchList(generics.ListCreateAPIView):
    queryset = Branch.objects.all()
    serializer_class = BranchSerializer


class BranchRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Branch.objects.all()
    serializer_class = BranchSerializer
