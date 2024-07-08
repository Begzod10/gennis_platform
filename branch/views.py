from rest_framework import generics
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from gennis_platform.permission import IsAdminOrReadOnly
from .serializers import (BranchSerializer, Branch)


class CreateBranchList(generics.ListCreateAPIView):
    queryset = Branch.objects.all()
    serializer_class = BranchSerializer
<<<<<<< HEAD
=======

    permission_classes = (
        IsAuthenticatedOrReadOnly, IsAdminOrReadOnly)

    # permission_classes = (
    #     IsAuthenticatedOrReadOnly, IsAdminOrReadOnly)
>>>>>>> 55b1efb65c1279aeaf68712f2b77d013d9849438


class BranchRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Branch.objects.all()
    serializer_class = BranchSerializer
<<<<<<< HEAD
=======

    permission_classes = (
        IsAuthenticatedOrReadOnly, IsAdminOrReadOnly)

    # permission_classes = (
    #     IsAuthenticatedOrReadOnly, IsAdminOrReadOnly)
    #
>>>>>>> 55b1efb65c1279aeaf68712f2b77d013d9849438
