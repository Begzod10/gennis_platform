from rest_framework import generics
from time_table.models import GroupTimeTable
from time_table.serializers import GroupTimeTableReadSerializer


class TimeTableRetrieveView(generics.RetrieveDestroyAPIView):
    queryset = GroupTimeTable.objects.all()
    serializer_class = GroupTimeTableReadSerializer
