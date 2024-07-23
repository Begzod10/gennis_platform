from rest_framework import generics
from group.models import Group
from group.serializers import GroupSerializer


class GroupProfile(generics.RetrieveUpdateAPIView):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
