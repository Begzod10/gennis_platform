from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from time_table.models import GroupTimeTable
from time_table.serializers import GroupTimeTableReadSerializer


class TimeTableRetrieveView(generics.RetrieveDestroyAPIView):
    permission_classes = [IsAuthenticated]

    queryset = GroupTimeTable.objects.all()
    serializer_class = GroupTimeTableReadSerializer
