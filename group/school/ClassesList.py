from rest_framework import generics
from rest_framework.response import Response

from group.models import Group
from group.serializers import GroupSerializer

from rest_framework.permissions import IsAuthenticated


class ClassesView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]

    queryset = Group.objects.filter(class_number__isnull=False)
    serializer_class = GroupSerializer
