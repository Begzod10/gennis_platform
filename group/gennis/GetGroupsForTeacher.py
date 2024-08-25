import json
from rest_framework import generics
from group.models import Group
from group.serializers import GroupSerializer


class GetGroupsForTeacher(generics.ListAPIView):
    serializer_class = GroupSerializer

    def get_queryset(self):
        teacher_id = self.kwargs['teacher_id']
        group_id = self.kwargs['group_id']
        return Group.objects.filter(teacher__in=[teacher_id]).exclude(id=group_id)
