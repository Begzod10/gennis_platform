import json
from rest_framework import generics
from group.models import Group
from group.serializers_list.serializers_self import GroupListSerializer
from rest_framework.permissions import IsAuthenticated

class GetGroupsForTeacher(generics.ListAPIView):
    permission_classes = [IsAuthenticated]

    serializer_class = GroupListSerializer

    def get_queryset(self):
        teacher_id = self.kwargs['teacher_id']
        group_id = self.kwargs['group_id']
        return Group.objects.filter(teacher__in=[teacher_id]).exclude(id=group_id)
