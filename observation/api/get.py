from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from observation.models import ObservationDay, ObservationStatistics
from observation.serializers import (ObservationDayListSerializers, ObservationStatisticsListSerializers,
                                     TeacherWeeklyObservationSerializer)

from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from group.models import Group
from observation.uitils import get_week_date_range
from school_time_table.models import ClassTimeTable
from teachers.models import Teacher
from observation.models import TeacherObservationDay, TeacherObservation, ObservationInfo, ObservationOptions
from django.utils.timezone import now
from datetime import datetime


def _complete_schedule_entry(observer_teacher, observed_teacher, observation_day):
    """
    Find the open TeacherObservationSchedule entry for this observer→observed_teacher
    pair in the latest cycle and mark it completed, linking the observation_day.
    """
    from observation.models import TeacherObservationCycle, TeacherObservationSchedule

    branch = observer_teacher.branches.first()
    if not branch:
        return

    cycle = (
        TeacherObservationCycle.objects
        .filter(branch=branch)
        .order_by('-created_at')
        .first()
    )
    if not cycle:
        return

    entry = (
        TeacherObservationSchedule.objects
        .filter(cycle=cycle, observer=observer_teacher, observed_teacher=observed_teacher, is_completed=False)
        .first()
    )
    if entry:
        entry.is_completed = True
        entry.observation_day = observation_day
        entry.save(update_fields=['is_completed', 'observation_day'])


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

        observer_teacher = Teacher.objects.filter(user=user, deleted=False).first()
        if observer_teacher and group.teacher:
            _complete_schedule_entry(observer_teacher, group.teacher, teacher_observation_day)

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
        print("date", date)
        print("group_id", group_id)
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
            days_list.append({"day": data.date.strftime("%d"), "id": data.id})
        days_list.sort(key=lambda x: x["day"])

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

    def get(self, request, group_id, observation_id):
        observation_list = []
        average = 0
        observer = {"name": "", "surname": ""}

        teacher_observation_day = TeacherObservationDay.objects.filter(
            id=observation_id, time_table_id=group_id
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
            "observation_id": teacher_observation_day.id if teacher_observation_day else None,
            "info": observation_list,
            "observation_options": list(ObservationOptions.objects.all().values("id", "name", "value")),
            "average": average,
            "observer": observer
        })

    def post(self, request, group_id, observation_id=None):
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

        observation_id = None

        if teacher_observation_day:
            observation_id = teacher_observation_day.id
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
            "observation_id": observation_id,
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


class WeeklyObservationStatsAPIView(APIView):
    """
    GET /observation/weekly/?cycle_id=1&branch_id=2
    """

    def get(self, request):
        from observation.models import TeacherObservationCycle, TeacherObservationSchedule

        cycle_id = request.query_params.get('cycle')
        branch_id = request.query_params.get('branch')

        if not cycle_id:
            return Response(
                {'detail': 'cycle_id majburiy.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            cycle = TeacherObservationCycle.objects.get(id=cycle_id)
        except TeacherObservationCycle.DoesNotExist:
            return Response({'detail': 'Cycle topilmadi.'}, status=status.HTTP_404_NOT_FOUND)

        schedules = (
            TeacherObservationSchedule.objects
            .filter(cycle=cycle)
            .select_related(
                'observer__user',
                'observed_teacher__user',
                'observation_day',
            )
        )

        if branch_id:
            schedules = schedules.filter(
                observed_teacher__user__branch_id=branch_id
            )

        # observed_teacher bo'yicha guruhlash
        teachers_map = {}
        for schedule in schedules:
            observed = schedule.observed_teacher
            tid = observed.id
            if tid not in teachers_map:
                user = observed.user
                teachers_map[tid] = {
                    'teacher_id': tid,
                    'teacher_name': f"{user.name or ''} {user.surname or ''}".strip(),
                    'observers': [],
                }
            teachers_map[tid]['observers'].append(schedule)

        result = []
        for data in teachers_map.values():
            observer_schedules = data['observers']
            completed = [s for s in observer_schedules if s.is_completed]
            pending = [s for s in observer_schedules if not s.is_completed]
            scores = [s.observation_day.average for s in completed if s.observation_day]

            result.append({
                **data,
                'total_observers_required': len(observer_schedules),
                'completed_count': len(completed),
                'pending_count': len(pending),
                'weekly_avg_score': round(sum(scores) / len(scores), 2) if scores else None,
            })
        from datetime import timedelta

        # Haftaning boshi (dushanba)
        week_start = cycle.start_date - timedelta(days=cycle.start_date.weekday())
        # Haftaning oxiri (yakshanba)
        week_end = week_start + timedelta(days=6)

        return Response({
            'cycle_id': cycle.id,
            'start_date': cycle.start_date,
            'end_date': week_end,  # ← shu, tamom
            'branch_id': cycle.branch_id,
            'teachers': TeacherWeeklyObservationSerializer(result, many=True).data,
        })
