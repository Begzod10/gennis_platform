from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from observation.models import ObservationDay, ObservationStatistics
from observation.serializers import (ObservationDayListSerializers, ObservationStatisticsListSerializers)

from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from group.models import Group
from school_time_table.models import ClassTimeTable
from teachers.models import Teacher
from observation.models import TeacherObservationDay, TeacherObservation, ObservationInfo, ObservationOptions
from django.utils.timezone import now
from datetime import datetime
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
class ObservedGroupAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, group_id, date=None):
        print ("date", date)
        print ("group_id", group_id)
        group = ClassTimeTable.objects.filter(id=group_id).first()
        if not group:
            return Response({"detail": "Group not found"}, status=404)

        days_list = []
        month_list = []
        years_list = []

        if date:
            calendar_month = datetime.strptime(date, "%Y-%m")
        else:
            calendar_month = datetime.now()

        teacher_observation_all = TeacherObservationDay.objects.filter(
            teacher_id=group.teacher_id,
            time_table=group_id
        ).order_by("id")

        teacher_observation = teacher_observation_all.filter(
            date__year=calendar_month.year,
            date__month=calendar_month.month
        )

        for data in teacher_observation:
            days_list.append(data.date.strftime("%d"))
        days_list.sort()

        for plan in teacher_observation_all:
            month_list.append(plan.date.strftime("%m"))
            years_list.append(plan.date.strftime("%Y"))

        month_list = sorted(list(dict.fromkeys(month_list)))
        years_list = sorted(list(dict.fromkeys(years_list)))

        return Response({
            "month_list": month_list,
            "years_list": years_list,
            "month": calendar_month.strftime("%m") if month_list else None,
            "year": calendar_month.strftime("%Y") if years_list else None,
            "days": days_list
        })
class ObservedGroupInfoAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, group_id):
        day = request.data.get("day")
        month = request.data.get("month")
        year = request.data.get("year")

        try:
            date = datetime.strptime(f"{year}-{month}-{day}", "%Y-%m-%d").date()
        except Exception:
            return Response({"detail": "Invalid date format"}, status=400)

        observation_list = []
        average = 0
        observer = {"name": "", "surname": ""}

        teacher_observation_day = TeacherObservationDay.objects.filter(
            date=date, time_table_id=group_id
        ).select_related("user").first()

        if teacher_observation_day:
            average = teacher_observation_day.average
            observer["name"] = teacher_observation_day.user.first_name if teacher_observation_day.user else ""
            observer["surname"] = teacher_observation_day.user.last_name if teacher_observation_day.user else ""

            observation_options = ObservationOptions.objects.all().order_by("id")
            observation_infos = ObservationInfo.objects.all().order_by("id")

            for info_item in observation_infos:
                teacher_obs = TeacherObservation.objects.filter(
                    observation_day=teacher_observation_day,
                    observation_info=info_item
                ).first()

                info = {
                    "title": info_item.title,
                    "values": [],
                    "comment": teacher_obs.comment if teacher_obs else ""
                }

                for option in observation_options:
                    teacher_obs_option = TeacherObservation.objects.filter(
                        observation_day=teacher_observation_day,
                        observation_info=info_item,
                        observation_options=option
                    ).select_related("observation_options").first()

                    info["values"].append({
                        "name": option.name,
                        "value": (
                            teacher_obs_option.observation_options.value
                            if teacher_obs_option and teacher_obs_option.observation_options
                            else ""
                        )
                    })

                observation_list.append(info)

        return Response({
            "info": observation_list,
            "observation_options": list(ObservationOptions.objects.all().values("id", "name", "value")),
            "average": average,
            "observer": observer
        })

class ObservedGroupClassroomAPIView(APIView):
    def get(self, request, group_id, date=None):
        group = get_object_or_404(ClassTimeTable, id=group_id)

        days_list = []
        month_list = []
        years_list = []

        if date and date != "None":
            try:
                calendar_month = datetime.strptime(date, "%Y-%m")
            except ValueError:
                return Response({"error": "Invalid date format, expected YYYY-MM"}, status=400)
        else:
            calendar_month = datetime.today()

        teacher_observation_all = TeacherObservationDay.objects.filter(
            teacher=group.teacher,
            time_table__group=group.group,
        ).order_by("id")

        teacher_observation = teacher_observation_all.filter(
            date__year=calendar_month.year,
            date__month=calendar_month.month
        )

        for data in teacher_observation:
            days_list.append(data.date.strftime("%d"))
        days_list.sort()

        for plan in teacher_observation_all:
            month_list.append(plan.date.strftime("%m"))
            years_list.append(plan.date.strftime("%Y"))

        month_list = sorted(list(dict.fromkeys(month_list)))
        years_list = sorted(list(dict.fromkeys(years_list)))

        if len(month_list) != 0:
            month = (
                calendar_month.strftime("%m")
                if month_list[-1] == calendar_month.strftime("%m")
                else month_list[-1]
            )
        else:
            month = calendar_month.strftime("%m")

        return Response({
            "month_list": month_list,
            "years_list": years_list,
            "month": month,
            "year": calendar_month.strftime("%Y"),
            "days": days_list
        })
class ObservedGroupInfoClassroomAPIView(APIView):


    def post(self, request, time_table_id):
        day = request.data.get('day')
        month = request.data.get('month')
        year = request.data.get('year')

        if not (day and month and year):
            return Response(
                {"error": "day, month, and year are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            date = datetime.strptime(f"{year}-{month}-{day}", "%Y-%m-%d").date()
        except ValueError:
            return Response(
                {"error": "Invalid date format."},
                status=status.HTTP_400_BAD_REQUEST
            )

        observation_options = ObservationOptions.objects.order_by("id").all()
        observation_infos = ObservationInfo.objects.order_by("id").all()

        observation_list = []
        average = 0
        observer = {"name": "", "surname": ""}

        teacher_observation_day = TeacherObservationDay.objects.filter(
            date=date,
            time_table_id=time_table_id
        ).select_related("user").first()

        if teacher_observation_day:
            average = teacher_observation_day.average
            observer["name"] = teacher_observation_day.user.name if teacher_observation_day.user else ""
            observer["surname"] = teacher_observation_day.user.surname if teacher_observation_day.user else ""

            for info_item in observation_infos:
                teacher_observation_comment = TeacherObservation.objects.filter(
                    observation_day=teacher_observation_day,
                    observation_info=info_item
                ).first()

                info_data = {
                    "title": info_item.title,
                    "values": [],
                    "comment": teacher_observation_comment.comment if teacher_observation_comment else "",
                }

                for option in observation_options:
                    teacher_obs = TeacherObservation.objects.filter(
                        observation_day=teacher_observation_day,
                        observation_info=info_item,
                        observation_options=option
                    ).first()

                    info_data["values"].append({
                        "name": option.name,
                        "value": teacher_obs.observation_options.value if teacher_obs and teacher_obs.observation_options else "",
                    })

                observation_list.append(info_data)

        return Response({
            "info": observation_list,
            "observation_options": [
                {"id": opt.id, "name": opt.name, "value": opt.value}
                for opt in observation_options
            ],
            "average": average,
            "observer": observer
        })