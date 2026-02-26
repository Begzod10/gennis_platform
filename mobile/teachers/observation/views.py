from datetime import datetime

from rest_framework import generics
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from observation.functions.creat_observation import creat_observation_info, creat_observation_options
from observation.models import ObservationInfo, ObservationOptions, TeacherObservationDay, TeacherObservation
from observation.serializers import ObservationInfoSerializers, ObservationOptionsSerializers
from school_time_table.models import ClassTimeTable


class ObservationInfoList(generics.ListAPIView):
    permission_classes = [IsAuthenticated]

    queryset = ObservationInfo.objects.all()
    serializer_class = ObservationInfoSerializers

    def get(self, request, *args, **kwargs):
        queryset = ObservationInfo.objects.all()
        serializer = ObservationInfoSerializers(queryset, many=True)
        creat_observation_info()
        return Response(serializer.data)


class ObservationOptionsList(generics.ListAPIView):
    permission_classes = [IsAuthenticated]

    queryset = ObservationOptions.objects.all()
    serializer_class = ObservationOptionsSerializers

    def get(self, request, *args, **kwargs):
        queryset = ObservationOptions.objects.all()
        serializer = ObservationOptionsSerializers(queryset, many=True)
        creat_observation_options()
        return Response(serializer.data)


class TeacherObserveView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, group_id):
        user = request.user
        group = get_object_or_404(ClassTimeTable, id=group_id)
        day = request.data.get('day', None)
        month = request.data.get('month', None)
        year = request.data.get('year', datetime.now().year)  # Agar yil berilmasa, hozirgi yilni oladi

        if day and month:
            date = datetime.strptime(f"{year}-{month}-{day}", '%Y-%m-%d').date()
        else:
            date = None

        teacher_observation_day, created = TeacherObservationDay.objects.get_or_create(
            teacher=group.teacher,
            time_table=group,
            date=date,
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
            .filter(time_table_id=group_id)
            .select_related("teacher", "time_table")
            .order_by("-date")
        )

        data = [
            {
                "id": obs.id,
                "date": obs.date,
                "average": obs.average,
                "teacher": obs.teacher.id if obs.teacher else None,
                "group": obs.time_table.id if obs.time_table else None,
            }
            for obs in observations
        ]

        return Response({
            "observation_tools": data,
            "old_current_dates": old_current_dates(group_id, observation=True)
        })
