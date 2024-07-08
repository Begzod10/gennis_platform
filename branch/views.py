from rest_framework import generics
from gennis_platform.permission import IsAdminOrReadOnly
from .serializers import (BranchSerializer, Branch)


class CreateBranchList(generics.ListCreateAPIView):
    queryset = Branch.objects.all()
    serializer_class = BranchSerializer
<<<<<<< HEAD
    # permission_classes = (
    #     IsAuthenticatedOrReadOnly, IsAdminOrReadOnly)
=======
    permission_classes = (
        IsAuthenticatedOrReadOnly, IsAdminOrReadOnly)
>>>>>>> 2398607749231d583f9f93f6743201907f04addb


class BranchRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Branch.objects.all()
    serializer_class = BranchSerializer
<<<<<<< HEAD
    # permission_classes = (
    #     IsAuthenticatedOrReadOnly, IsAdminOrReadOnly)
    #
=======
    permission_classes = (
        IsAuthenticatedOrReadOnly, IsAdminOrReadOnly)
>>>>>>> 2398607749231d583f9f93f6743201907f04addb
