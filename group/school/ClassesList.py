from rest_framework import generics
from rest_framework.response import Response

from group.models import Group
from group.serializers import GroupSerializer


class ClassesView(generics.ListCreateAPIView):
    queryset = Group.objects.filter(class_number__isnull=False)
    serializer_class = GroupSerializer
