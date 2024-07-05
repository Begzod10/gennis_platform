from django.shortcuts import render

# Create your views here.

from .forms import BranchForm
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response

from rest_framework import generics
from rest_framework.permissions import *
from gennis_platform.permission import IsAdminOrReadOnly
from .serializers import *


class CreateBranchList(generics.ListCreateAPIView):
    queryset = Branch.objects.all()
    serializer_class = BranchSerializers
    permission_classes = (
        IsAuthenticatedOrReadOnly, IsAdminOrReadOnly)


class BranchRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Branch.objects.all()
    serializer_class = BranchSerializers
    permission_classes = (
        IsAuthenticatedOrReadOnly, IsAdminOrReadOnly)
