from datetime import date, timedelta

from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiParameter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from observation.models import TeacherObservationCycle, TeacherObservationSchedule
from teachers.models import Teacher


def _get_current_week(cycle: TeacherObservationCycle) -> int:
    delta = (date.today() - cycle.start_date).days
    return max(1, delta // 7 + 1)


def _fmt(entry: TeacherObservationSchedule) -> dict:
    tt = entry.time_table
    return {
        "id": entry.id,
        "week": entry.week,
        "is_completed": entry.is_completed,
        "observed_teacher": {
            "id": entry.observed_teacher_id,
            "name": entry.observed_teacher.user.name if entry.observed_teacher.user else "",
            "surname": entry.observed_teacher.user.surname if entry.observed_teacher.user else "",
        },
        "time_table": {"id": tt.id, "name": tt.name} if tt else None,
        "observation_day_id": entry.observation_day_id,
    }


class MobileTeacherScheduleView(APIView):
    """
    GET /mobile/teachers/observation/schedule/

    Returns the observation schedule for the authenticated teacher.
    Uses the latest cycle of the teacher's first branch.

    Query params:
      - week (int, optional): specific week number; defaults to current week
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        parameters=[
            OpenApiParameter("week", int, description="Week number (default: current week)"),
        ],
        responses={200: dict},
        examples=[
            OpenApiExample(
                "Current week schedule",
                value={
                    "current_week": 2,
                    "total_weeks": 5,
                    "week": 2,
                    "week_start": "2026-04-28",
                    "cycle_start": "2026-04-21",
                    "schedule": [
                        {
                            "id": 11,
                            "week": 2,
                            "is_completed": False,
                            "observed_teacher": {
                                "id": 4,
                                "name": "Jasur",
                                "surname": "Toshev"
                            },
                            "time_table": {"id": 22, "name": "Matematika 9A"},
                            "observation_day_id": None
                        },
                        {
                            "id": 12,
                            "week": 2,
                            "is_completed": True,
                            "observed_teacher": {
                                "id": 5,
                                "name": "Malika",
                                "surname": "Yusupova"
                            },
                            "time_table": {"id": 31, "name": "Ingliz tili 8B"},
                            "observation_day_id": 7
                        }
                    ]
                },
                response_only=True,
            )
        ],
        summary="Teacher's observation schedule (current/specific week)",
        tags=["mobile-observation"],
    )
    def get(self, request):
        try:
            teacher = Teacher.objects.filter(user=request.user, deleted=False).first()
        except Teacher.DoesNotExist:
            return Response({"detail": "Teacher not found."}, status=404)

        if not teacher:
            return Response({"detail": "Teacher not found."}, status=404)

        branch = teacher.branches.first()
        if not branch:
            return Response({"detail": "Teacher has no branch assigned."}, status=400)

        cycle = (
            TeacherObservationCycle.objects
            .filter(branch=branch)
            .order_by("-created_at")
            .first()
        )
        if not cycle:
            return Response({"detail": "No observation cycle found for your branch."}, status=404)

        current_week = _get_current_week(cycle)
        requested_week = int(request.query_params.get("week", current_week))

        entries = (
            TeacherObservationSchedule.objects
            .filter(cycle=cycle, observer=teacher, week=requested_week)
            .select_related("observed_teacher__user", "time_table")
        )

        total_weeks = (
            TeacherObservationSchedule.objects
            .filter(cycle=cycle, observer=teacher)
            .order_by("-week")
            .values_list("week", flat=True)
            .first() or 0
        )

        return Response({
            "current_week": current_week,
            "total_weeks": total_weeks,
            "week": requested_week,
            "week_start": (cycle.start_date + timedelta(weeks=requested_week - 1)).isoformat(),
            "cycle_start": cycle.start_date.isoformat(),
            "schedule": [_fmt(e) for e in entries],
        })


class MobileTeacherFullScheduleView(APIView):
    """
    GET /mobile/teachers/observation/schedule/all/

    Returns the full schedule (all weeks) for the authenticated teacher,
    grouped by week.
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: dict},
        examples=[
            OpenApiExample(
                "Full schedule",
                value={
                    "current_week": 2,
                    "cycle_start": "2026-04-21",
                    "weeks": [
                        {
                            "week": 1,
                            "week_start": "2026-04-21",
                            "is_current": False,
                            "entries": [
                                {
                                    "id": 1,
                                    "week": 1,
                                    "is_completed": True,
                                    "observed_teacher": {"id": 2, "name": "Dilnoza", "surname": "Rahimova"},
                                    "time_table": {"id": 10, "name": "Tarix 7A"},
                                    "observation_day_id": 5
                                }
                            ]
                        },
                        {
                            "week": 2,
                            "week_start": "2026-04-28",
                            "is_current": True,
                            "entries": [
                                {
                                    "id": 11,
                                    "week": 2,
                                    "is_completed": False,
                                    "observed_teacher": {"id": 4, "name": "Jasur", "surname": "Toshev"},
                                    "time_table": {"id": 22, "name": "Matematika 9A"},
                                    "observation_day_id": None
                                }
                            ]
                        }
                    ]
                },
                response_only=True,
            )
        ],
        summary="Teacher's full observation schedule (all weeks)",
        tags=["mobile-observation"],
    )
    def get(self, request):
        teacher = Teacher.objects.filter(user=request.user, deleted=False).first()
        if not teacher:
            return Response({"detail": "Teacher not found."}, status=404)

        branch = teacher.branches.first()
        if not branch:
            return Response({"detail": "Teacher has no branch assigned."}, status=400)

        cycle = (
            TeacherObservationCycle.objects
            .filter(branch=branch)
            .order_by("-created_at")
            .first()
        )
        if not cycle:
            return Response({"detail": "No observation cycle found for your branch."}, status=404)

        current_week = _get_current_week(cycle)

        entries = (
            TeacherObservationSchedule.objects
            .filter(cycle=cycle, observer=teacher)
            .select_related("observed_teacher__user", "time_table")
            .order_by("week", "id")
        )

        grouped = {}
        for e in entries:
            grouped.setdefault(e.week, []).append(_fmt(e))

        weeks = [
            {
                "week": w,
                "week_start": (cycle.start_date + timedelta(weeks=w - 1)).isoformat(),
                "is_current": w == current_week,
                "entries": items,
            }
            for w, items in sorted(grouped.items())
        ]

        return Response({
            "current_week": current_week,
            "cycle_start": cycle.start_date.isoformat(),
            "weeks": weeks,
        })


class MobileCompleteObservationView(APIView):
    """
    PATCH /mobile/teachers/observation/schedule/<id>/complete/

    Mark an observation schedule entry as completed.
    Optionally link it to a TeacherObservationDay record.
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=dict,
        responses={200: dict},
        examples=[
            OpenApiExample(
                "Request",
                value={"observation_day_id": 9},
                request_only=True,
            ),
            OpenApiExample(
                "Response",
                value={
                    "id": 11,
                    "week": 2,
                    "is_completed": True,
                    "observed_teacher": {"id": 4, "name": "Jasur", "surname": "Toshev"},
                    "time_table": {"id": 22, "name": "Matematika 9A"},
                    "observation_day_id": 9
                },
                response_only=True,
            )
        ],
        summary="Mark observation schedule entry as completed",
        tags=["mobile-observation"],
    )
    def patch(self, request, pk):
        teacher = Teacher.objects.filter(user=request.user, deleted=False).first()
        if not teacher:
            return Response({"detail": "Teacher not found."}, status=404)

        try:
            entry = TeacherObservationSchedule.objects.select_related(
                "observed_teacher__user", "time_table"
            ).get(pk=pk, observer=teacher)
        except TeacherObservationSchedule.DoesNotExist:
            return Response({"detail": "Schedule entry not found."}, status=404)

        observation_day_id = request.data.get("observation_day_id")
        if observation_day_id:
            entry.observation_day_id = observation_day_id

        entry.is_completed = True
        entry.save(update_fields=["is_completed", "observation_day_id"])

        return Response(_fmt(entry))
