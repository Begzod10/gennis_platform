from rest_framework import generics
from observation.serializers import ObservationDaySerializers, ObservationStatisticsSerializers
from observation.models import ObservationDay, ObservationStatistics


class ObservationStatisticsCreateView(generics.CreateAPIView):
    queryset = ObservationStatistics.objects.all()
    serializer_class = ObservationStatisticsSerializers


class ObservationStatisticsUpdateView(generics.UpdateAPIView):
    queryset = ObservationStatistics.objects.all()
    serializer_class = ObservationStatisticsSerializers


class ObservationStatisticsDestroyView(generics.DestroyAPIView):
    queryset = ObservationStatistics.objects.all()
    serializer_class = ObservationStatisticsSerializers


class ObservationDayCreateView(generics.CreateAPIView):
    queryset = ObservationDay.objects.all()
    serializer_class = ObservationDaySerializers


class ObservationDayUpdateView(generics.UpdateAPIView):
    queryset = ObservationDay.objects.all()
    serializer_class = ObservationDaySerializers


class ObservationDayDestroyView(generics.DestroyAPIView):
    queryset = ObservationDay.objects.all()
    serializer_class = ObservationDaySerializers
