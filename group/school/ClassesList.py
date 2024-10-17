from rest_framework import generics
from rest_framework.response import Response

from group.models import Group
from group.serializers import GroupSerializer

from rest_framework.permissions import IsAuthenticated


class ClassesView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]

    queryset = Group.objects.filter(class_number__isnull=False)
    serializer_class = GroupSerializer
    fields = ['id', 'user__name', 'user__surname', 'user__username', 'class_number__number', 'user__birth_date',
              'user__language__name', 'user__branch__name', 'subject__name', 'user__registered_date', 'user__age']

    def get_serializer(self, *args, **kwargs):
        kwargs['context'] = self.get_serializer_context()
        kwargs['context']['fields'] = self.fields
        return super().get_serializer(*args, **kwargs)
