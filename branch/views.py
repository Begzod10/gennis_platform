from rest_framework import generics
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from gennis_platform.permission import IsAdminOrReadOnly
from .serializers import (BranchSerializer, Branch)


class CreateBranchList(generics.ListCreateAPIView):
    queryset = Branch.objects.all()
    serializer_class = BranchSerializer

    permission_classes = (
        IsAuthenticatedOrReadOnly, IsAdminOrReadOnly)

    # permission_classes = (
    #     IsAuthenticatedOrReadOnly, IsAdminOrReadOnly)


class BranchRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Branch.objects.all()
    serializer_class = BranchSerializer

    permission_classes = (
        IsAuthenticatedOrReadOnly, IsAdminOrReadOnly)

    # permission_classes = (
    #     IsAuthenticatedOrReadOnly, IsAdminOrReadOnly)
    #
