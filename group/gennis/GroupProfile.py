from rest_framework import generics
from group.models import Group
from group.serializers import GroupSerializer, GroupCreateUpdateSerializer
from rest_framework.response import Response


class GroupProfile(generics.RetrieveUpdateAPIView):
    queryset = Group.objects.all()
    serializer_class = GroupCreateUpdateSerializer

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return GroupCreateUpdateSerializer
        return GroupSerializer

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        instance.refresh_from_db()
        read_serializer = GroupSerializer(instance)
        return Response(read_serializer.data)
