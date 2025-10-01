from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from observation.models import ObservationDay, ObservationStatistics
from observation.serializers import (ObservationDayListSerializers, ObservationStatisticsListSerializers)

from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from group.models import Group
from teachers.models import Teacher
from observation.models import TeacherObservationDay, TeacherObservation, ObservationInfo, ObservationOptions
from django.utils.timezone import now
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
class TeacherObserveView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, group_id):
        user = request.user
        group = get_object_or_404(Group, id=group_id)

        today = now().date()

        teacher_observation_day, created = TeacherObservationDay.objects.get_or_create(
            teacher=group.teacher,
            group=group,
            date=today,
            defaults={"user": user}
        )

        result = 0
        for item in request.data.get("list", []):
            observation_options = get_object_or_404(ObservationOptions, id=item.get("value"))
            result += observation_options.value

            TeacherObservation.objects.update_or_create(
                observation_info_id=item.get("id"),
                observation_day=teacher_observation_day,
                defaults={
                    "observation_options": observation_options,
                    "comment": item.get("comment", "")
                }
            )

        observation_infos = ObservationInfo.objects.count()
        if observation_infos > 0:
            avg = round(result / observation_infos)
            teacher_observation_day.average = avg
            teacher_observation_day.save()

        return Response({"msg": "Teacher has been observed", "success": True})

    def get(self, request, group_id):
        from observation.uitils import old_current_dates

        observations = (
            TeacherObservationDay.objects
            .filter(group_id=group_id)
            .select_related("teacher", "group")
            .order_by("-date")
        )

        data = [
            {
                "id": obs.id,
                "date": obs.date,
                "average": obs.average,
                "teacher": obs.teacher.id if obs.teacher else None,
                "group": obs.group.id if obs.group else None,
            }
            for obs in observations
        ]

        return Response({
            "observation_tools": data,
            "old_current_dates": old_current_dates(group_id=group_id, observation=True)
        })
