from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from time_table.models import TimeTableArchive
from time_table.serializers import TimeTableArchiveListSerializer


class TimeTableArchiveRetrieveAPIView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]

    queryset = TimeTableArchive.objects.all()
    serializer_class = TimeTableArchiveListSerializer

    def retrieve(self, request, *args, **kwargs):
        time_table_archive = self.get_object()
        time_table_archive_data = self.get_serializer(time_table_archive).data
        return Response(time_table_archive_data)


class TimeTableArchiveListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]

    queryset = TimeTableArchive.objects.all()
    serializer_class = TimeTableArchiveListSerializer

    def get(self, request, *args, **kwargs):
        queryset = TimeTableArchive.objects.all()

        serializer = TimeTableArchiveListSerializer(queryset, many=True)
        return Response(serializer.data)
