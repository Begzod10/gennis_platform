from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from observation.models import ObservationDay, ObservationStatistics
from observation.serializers import (ObservationDayListSerializers, ObservationStatisticsListSerializers)


class ObservationStatisticsRetrieveAPIView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]

    queryset = ObservationStatistics.objects.all()
    serializer_class = ObservationStatisticsListSerializers

    def retrieve(self, request, *args, **kwargs):
        observation_statistics = self.get_object()
        observation_statistics_data = self.get_serializer(observation_statistics).data
        return Response(observation_statistics_data)


class ObservationStatisticsListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]

    queryset = ObservationStatistics.objects.all()
    serializer_class = ObservationStatisticsListSerializers

    def get(self, request, *args, **kwargs):

        queryset = ObservationStatistics.objects.all()
        location_id = self.request.query_params.get('location_id', None)
        branch_id = self.request.query_params.get('branch_id', None)

        if branch_id is not None:
            queryset = queryset.filter(branch_id=branch_id)
        if location_id is not None:
            queryset = queryset.filter(location_id=location_id)
        serializer = ObservationStatisticsListSerializers(queryset, many=True)
        return Response(serializer.data)


class ObservationDayRetrieveAPIView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]

    queryset = ObservationDay.objects.all()
    serializer_class = ObservationDayListSerializers

    def retrieve(self, request, *args, **kwargs):
        observation_day = self.get_object()
        observation_day_data = self.get_serializer(observation_day).data
        return Response(observation_day_data)


class ObservationDayListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]

    queryset = ObservationDay.objects.all()
    serializer_class = ObservationDayListSerializers

    def get(self, request, *args, **kwargs):

        queryset = ObservationDay.objects.all()
        location_id = self.request.query_params.get('location_id', None)
        branch_id = self.request.query_params.get('branch_id', None)

        if branch_id is not None:
            queryset = queryset.filter(branch_id=branch_id)
        if location_id is not None:
            queryset = queryset.filter(location_id=location_id)
        serializer = ObservationDayListSerializers(queryset, many=True)
        return Response(serializer.data)
