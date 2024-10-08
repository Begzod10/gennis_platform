from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from time_table.models import GroupTimeTable
from time_table.serializers import GroupTimeTableCreateUpdateSerializer


class GroupTimeTableUpdate(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]

    queryset = GroupTimeTable.objects.all()
    serializer_class = GroupTimeTableCreateUpdateSerializer

    # def update(self, request, *args, **kwargs):
    #     write_serializer = self.get_serializer(data=request.data, partial=True)
    #     write_serializer.is_valid(raise_exception=True)
    #     self.perform_update(write_serializer)
    #
    #     instance = GroupTimeTable.objects.get(pk=write_serializer.data['id'])
    #     read_serializer = GroupTimeTableReadSerializer(instance)
    #
    #     return Response(read_serializer.data)
