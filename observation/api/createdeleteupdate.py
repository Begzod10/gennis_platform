from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404

from observation.models import ObservationDay, ObservationStatistics, TeacherObservationDay, TeacherObservation
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


class TeacherObservationDayDestroyView(APIView):
    """
    DELETE /teacher_observation_day_delete/<int:pk>/
    Deletes a TeacherObservationDay and all its related TeacherObservation records.
    """
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        obj = get_object_or_404(TeacherObservationDay, pk=pk)
        TeacherObservation.objects.filter(observation_day=obj).delete()
        obj.delete()
        return Response({"success": True}, status=status.HTTP_200_OK)
