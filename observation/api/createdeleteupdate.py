from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from observation.models import ObservationDay, ObservationStatistics
from observation.serializers import ObservationDaySerializers, ObservationStatisticsSerializers


class ObservationStatisticsCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]

    queryset = ObservationStatistics.objects.all()
    serializer_class = ObservationStatisticsSerializers


class ObservationStatisticsUpdateView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]

    queryset = ObservationStatistics.objects.all()
    serializer_class = ObservationStatisticsSerializers


class ObservationStatisticsDestroyView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]

    queryset = ObservationStatistics.objects.all()
    serializer_class = ObservationStatisticsSerializers


class ObservationDayCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]

    queryset = ObservationDay.objects.all()
    serializer_class = ObservationDaySerializers


class ObservationDayUpdateView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]

    queryset = ObservationDay.objects.all()
    serializer_class = ObservationDaySerializers


class ObservationDayDestroyView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]

    queryset = ObservationDay.objects.all()
    serializer_class = ObservationDaySerializers
