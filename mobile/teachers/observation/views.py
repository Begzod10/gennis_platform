from datetime import date
from datetime import datetime

from rest_framework import generics, status
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from observation.functions.creat_observation import creat_observation_info, creat_observation_options
from observation.models import ObservationInfo, ObservationOptions, TeacherObservationDay, TeacherObservation
from observation.serializers import ObservationInfoSerializers, ObservationOptionsSerializers
from observation.uitils import old_current_dates
from school_time_table.models import ClassTimeTable
from teachers.models import Teacher


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


class TeacherObserveGroupView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):

        if not request.user.observer:
            return Response(
                {"detail": "Ruxsat yo'q"},
                status=status.HTTP_403_FORBIDDEN
            )
        teacher =Teacher.objects.filter(user=request.user).first()
        if not teacher:
            return Response(
                {"detail": "Teacher mavjud emas"},
                status=status.HTTP_400_BAD_REQUEST
            )

        day = request.query_params.get('day')
        month = request.query_params.get('month')
        year = request.query_params.get('year')

        try:
            if day and month:
                year = int(year) if year else date.today().year
                today = date(int(year), int(month), int(day))
            elif not day and not month and not year:
                today = date.today()
            else:
                return Response(
                    {"detail": "To'liq sana yuboring (day, month, year)"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except (ValueError, TypeError):
            return Response(
                {"detail": "Noto'g'ri sana formati"},
                status=status.HTTP_400_BAD_REQUEST
            )

        groups = ClassTimeTable.objects.select_related(
            'group',
            'group__class_number',
            'group__class_type',
            'subject',
            'teacher__user',
            'flow'
        ).filter(
            date=today
        )

        data = []

        for obj in groups:
            name = None
            if obj.group:
                if obj.group.name:
                    name = obj.group.name
                elif obj.group.class_number and obj.group.class_type:
                    name = f"{obj.group.class_number.number} {obj.group.class_type.name}"

            data.append({
                "id": obj.id,
                "name": name,
                "subject": obj.subject.name if obj.subject else None,
                "teacher": f"{obj.teacher.user.name} {obj.teacher.user.surname}" if obj.teacher else None,
                "flow": obj.flow.name if obj.flow else None,
                "type": "flow" if obj.flow else "group",
                "is_flow": bool(obj.flow),
            })

        return Response({"groups": data, "old_current_dates": old_current_dates(0, observation=True)})
