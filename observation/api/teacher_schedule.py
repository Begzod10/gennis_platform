from datetime import date, timedelta

from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiParameter
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from observation.models import TeacherObservationCycle, TeacherObservationSchedule
from teachers.models import Teacher


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_current_week(cycle: TeacherObservationCycle) -> int:
    """Return 1-based week number relative to cycle start_date."""
    delta = (date.today() - cycle.start_date).days
    if delta < 0:
        return 1
    return delta // 7 + 1


def _teacher_info(teacher: Teacher) -> dict:
    return {
        "id": teacher.id,
        "name": teacher.user.name if teacher.user else "",
        "surname": teacher.user.surname if teacher.user else "",
    }


def _schedule_entry(entry: TeacherObservationSchedule) -> dict:
    time_table = entry.time_table
    return {
        "id": entry.id,
        "week": entry.week,
        "observed_teacher": _teacher_info(entry.observed_teacher),
        "observer": _teacher_info(entry.observer),
        "is_completed": entry.is_completed,
        "time_table": {
            "id": time_table.id,
            "name": time_table.name,
        } if time_table else None,
        "observation_day_id": entry.observation_day_id,
    }


# ---------------------------------------------------------------------------
# Generate schedule  (dispatched to Celery)
# ---------------------------------------------------------------------------

class GenerateObservationScheduleView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request={"application/json": {"type": "object", "properties": {
            "branch_id": {"type": "integer", "example": 1},
            "start_date": {"type": "string", "example": "2026-04-21"},
        }, "required": ["branch_id", "start_date"]}},
        responses={202: dict},
        examples=[
            OpenApiExample("Request", value={"branch_id": 1, "start_date": "2026-04-21"}, request_only=True),
            OpenApiExample("Response", value={"task_id": "abc-123", "detail": "Schedule generation started."}, response_only=True),
        ],
        summary="Generate observation schedule for a branch",
        tags=["observation-schedule"],
    )
    def post(self, request):
        from observation.tasks import generate_observation_schedule_task

        branch_id = request.data.get("branch_id")
        start_date_str = request.data.get("start_date")

        if not branch_id or not start_date_str:
            return Response(
                {"detail": "branch_id and start_date are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validate date format before handing off to Celery
        try:
            date.fromisoformat(start_date_str)
        except ValueError:
            return Response({"detail": "start_date must be YYYY-MM-DD."}, status=400)

        task = generate_observation_schedule_task.delay(
            branch_id=int(branch_id),
            start_date_str=start_date_str,
        )

        return Response(
            {
                "task_id": task.id,
                "detail": "Schedule generation started.",
            },
            status=status.HTTP_202_ACCEPTED,
        )


# ---------------------------------------------------------------------------
# Task status
# ---------------------------------------------------------------------------

class ScheduleTaskStatusView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: dict},
        examples=[
            OpenApiExample("Pending", value={"task_id": "abc-123", "state": "PENDING"}, response_only=True),
            OpenApiExample("Success", value={"task_id": "abc-123", "state": "SUCCESS", "result": {"created": 40}}, response_only=True),
            OpenApiExample("Failure", value={"task_id": "abc-123", "state": "FAILURE", "detail": "Branch not found."}, response_only=True),
        ],
        summary="Check Celery task status",
        tags=["observation-schedule"],
    )
    def get(self, request, task_id):
        from celery.result import AsyncResult
        result = AsyncResult(task_id)

        payload = {"task_id": task_id, "state": result.state}

        if result.state == "SUCCESS":
            payload["result"] = result.result
        elif result.state == "FAILURE":
            payload["detail"] = str(result.result)

        return Response(payload)


# ---------------------------------------------------------------------------
# Current-week schedule for one teacher
# ---------------------------------------------------------------------------

class CurrentWeekScheduleView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        parameters=[
            OpenApiParameter("branch_id", int, description="Branch ID"),
            OpenApiParameter("teacher_id", int, description="Observer teacher ID"),
        ],
        responses={200: dict},
        examples=[
            OpenApiExample("Response", value={
                "cycle_id": 1, "current_week": 2,
                "schedule": [
                    {"id": 5, "week": 2, "is_completed": False,
                     "observer": {"id": 3, "name": "Ali", "surname": "Valiev"},
                     "observed_teacher": {"id": 7, "name": "Jasur", "surname": "Toshev"},
                     "time_table": {"id": 12, "name": "Matematika 9A"}, "observation_day_id": None},
                ]
            }, response_only=True),
        ],
        summary="Current week schedule for a teacher",
        tags=["observation-schedule"],
    )
    def get(self, request):
        branch_id = request.query_params.get("branch_id")
        teacher_id = request.query_params.get("teacher_id")

        if not branch_id or not teacher_id:
            return Response({"detail": "branch_id and teacher_id are required."}, status=400)

        cycle = (
            TeacherObservationCycle.objects.filter(branch_id=branch_id)
            .order_by("-created_at")
            .first()
        )
        if not cycle:
            return Response({"detail": "No observation cycle found for this branch."}, status=404)

        current_week = _get_current_week(cycle)

        entries = (
            TeacherObservationSchedule.objects.filter(
                cycle=cycle, observer_id=teacher_id, week=current_week
            )
            .select_related("observed_teacher__user", "observer__user", "time_table")
        )

        return Response(
            {
                "cycle_id": cycle.id,
                "current_week": current_week,
                "schedule": [_schedule_entry(e) for e in entries],
            }
        )


# ---------------------------------------------------------------------------
# Full schedule list for one observer teacher
# ---------------------------------------------------------------------------

class TeacherScheduleListView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        parameters=[
            OpenApiParameter("branch_id", int, description="Branch ID"),
            OpenApiParameter("teacher_id", int, description="Observer teacher ID"),
            OpenApiParameter("cycle_id", int, description="Cycle ID (optional, defaults to latest)"),
        ],
        responses={200: dict},
        examples=[
            OpenApiExample("Response", value={
                "cycle_id": 1, "start_date": "2026-04-21", "current_week": 2,
                "weeks": [
                    {"week": 1, "week_start": "2026-04-21", "is_current": False,
                     "entries": [{"id": 1, "week": 1, "is_completed": True,
                                  "observer": {"id": 3, "name": "Ali", "surname": "Valiev"},
                                  "observed_teacher": {"id": 7, "name": "Jasur", "surname": "Toshev"},
                                  "time_table": {"id": 12, "name": "Matematika 9A"}, "observation_day_id": 5}]},
                    {"week": 2, "week_start": "2026-04-28", "is_current": True,
                     "entries": [{"id": 5, "week": 2, "is_completed": False,
                                  "observer": {"id": 3, "name": "Ali", "surname": "Valiev"},
                                  "observed_teacher": {"id": 9, "name": "Malika", "surname": "Yusupova"},
                                  "time_table": {"id": 18, "name": "Ingliz tili 8B"}, "observation_day_id": None}]},
                ]
            }, response_only=True),
        ],
        summary="Full observation schedule (all weeks) for a teacher",
        tags=["observation-schedule"],
    )
    def get(self, request):
        branch_id = request.query_params.get("branch_id")
        teacher_id = request.query_params.get("teacher_id")
        cycle_id = request.query_params.get("cycle_id")

        if not branch_id or not teacher_id:
            return Response({"detail": "branch_id and teacher_id are required."}, status=400)

        if cycle_id:
            cycle = get_object_or_404(TeacherObservationCycle, id=cycle_id, branch_id=branch_id)
        else:
            cycle = (
                TeacherObservationCycle.objects.filter(branch_id=branch_id)
                .order_by("-created_at")
                .first()
            )
            if not cycle:
                return Response({"detail": "No observation cycle found for this branch."}, status=404)

        entries = (
            TeacherObservationSchedule.objects.filter(cycle=cycle, observer_id=teacher_id)
            .select_related("observed_teacher__user", "observer__user", "time_table")
            .order_by("week", "id")
        )

        current_week = _get_current_week(cycle)

        grouped = {}
        for entry in entries:
            grouped.setdefault(entry.week, []).append(_schedule_entry(entry))

        weeks = [
            {
                "week": week,
                "week_start": (cycle.start_date + timedelta(weeks=week - 1)).isoformat(),
                "is_current": week == current_week,
                "entries": items,
            }
            for week, items in sorted(grouped.items())
        ]

        return Response(
            {
                "cycle_id": cycle.id,
                "start_date": cycle.start_date.isoformat(),
                "current_week": current_week,
                "weeks": weeks,
            }
        )


# ---------------------------------------------------------------------------
# Mark an observation as complete
# ---------------------------------------------------------------------------

class CompleteObservationScheduleView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request={"application/json": {"type": "object", "properties": {
            "observation_day_id": {"type": "integer", "example": 9},
        }}},
        responses={200: dict},
        examples=[
            OpenApiExample("Request", value={"observation_day_id": 9}, request_only=True),
            OpenApiExample("Response", value={
                "id": 5, "week": 2, "is_completed": True,
                "observer": {"id": 3, "name": "Ali", "surname": "Valiev"},
                "observed_teacher": {"id": 7, "name": "Jasur", "surname": "Toshev"},
                "time_table": {"id": 12, "name": "Matematika 9A"}, "observation_day_id": 9
            }, response_only=True),
        ],
        summary="Mark observation schedule entry as completed",
        tags=["observation-schedule"],
    )
    def patch(self, request, pk):
        entry = get_object_or_404(
            TeacherObservationSchedule.objects.select_related(
                "observed_teacher__user", "observer__user", "time_table"
            ),
            pk=pk,
        )

        observation_day_id = request.data.get("observation_day_id")
        if observation_day_id:
            entry.observation_day_id = observation_day_id

        entry.is_completed = True
        entry.save(update_fields=["is_completed", "observation_day_id"])

        return Response(_schedule_entry(entry))


# ---------------------------------------------------------------------------
# List all cycles for a branch
# ---------------------------------------------------------------------------

class TestGenerateScheduleView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request={"application/json": {"type": "object", "properties": {
            "branch_id": {"type": "integer", "example": 1},
        }, "required": ["branch_id"]}},
        responses={202: dict},
        examples=[
            OpenApiExample("Request", value={"branch_id": 1}, request_only=True),
            OpenApiExample("Response", value={"task_id": "def-456", "detail": "Test schedule generation started."}, response_only=True),
        ],
        summary="Test generate schedule using current week's Monday as start_date",
        tags=["observation-schedule"],
    )
    def post(self, request):
        from observation.tasks import test_generate_observation_schedule_task

        branch_id = request.data.get("branch_id")
        if not branch_id:
            return Response({"detail": "branch_id is required."}, status=400)

        task = test_generate_observation_schedule_task.delay(branch_id=int(branch_id))
        return Response(
            {"task_id": task.id, "detail": "Test schedule generation started."},
            status=status.HTTP_202_ACCEPTED,
        )


class ObservationCycleListView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        parameters=[OpenApiParameter("branch_id", int, description="Branch ID")],
        responses={200: dict},
        examples=[
            OpenApiExample("Response", value=[
                {"id": 1, "branch_id": 1, "start_date": "2026-04-21", "created_at": "2026-04-21T08:00:00Z",
                 "total_schedules": 40, "completed": 12},
                {"id": 2, "branch_id": 1, "start_date": "2026-01-06", "created_at": "2026-01-06T08:00:00Z",
                 "total_schedules": 38, "completed": 38},
            ], response_only=True),
        ],
        summary="List all observation cycles for a branch",
        tags=["observation-schedule"],
    )
    def get(self, request):
        branch_id = request.query_params.get("branch_id")
        if not branch_id:
            return Response({"detail": "branch_id is required."}, status=400)

        cycles = TeacherObservationCycle.objects.filter(branch_id=branch_id).order_by("-created_at")

        data = [
            {
                "id": c.id,
                "branch_id": c.branch_id,
                "start_date": c.start_date.isoformat(),
                "created_at": c.created_at.isoformat(),
                "total_schedules": c.schedules.count(),
                "completed": c.schedules.filter(is_completed=True).count(),
            }
            for c in cycles
        ]
        return Response(data)


# ---------------------------------------------------------------------------
# Branch-wide schedule — all observers for a given week
# ---------------------------------------------------------------------------

class BranchScheduleView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        parameters=[
            OpenApiParameter("branch_id", int, description="Branch ID"),
            OpenApiParameter("week", int, description="Week number (default: current week)"),
            OpenApiParameter("cycle_id", int, description="Cycle ID (optional, defaults to latest)"),
        ],
        responses={200: dict},
        examples=[
            OpenApiExample("Response", value={
                "cycle_id": 1, "start_date": "2026-04-21", "current_week": 2, "week": 2,
                "week_start": "2026-04-28",
                "observers": [
                    {"observer": {"id": 3, "name": "Ali", "surname": "Valiev"},
                     "assignments": [
                         {"id": 5, "week": 2, "is_completed": False,
                          "observer": {"id": 3, "name": "Ali", "surname": "Valiev"},
                          "observed_teacher": {"id": 7, "name": "Jasur", "surname": "Toshev"},
                          "time_table": {"id": 12, "name": "Matematika 9A"}, "observation_day_id": None},
                     ]},
                ]
            }, response_only=True),
        ],
        summary="Branch-wide schedule — all observers for a week",
        tags=["observation-schedule"],
    )
    def get(self, request):
        branch_id = request.query_params.get("branch_id")
        if not branch_id:
            return Response({"detail": "branch_id is required."}, status=400)

        cycle_id = request.query_params.get("cycle_id")
        if cycle_id:
            cycle = get_object_or_404(TeacherObservationCycle, id=cycle_id, branch_id=branch_id)
        else:
            cycle = (
                TeacherObservationCycle.objects.filter(branch_id=branch_id)
                .order_by("-created_at")
                .first()
            )
            if not cycle:
                return Response({"detail": "No observation cycle found for this branch."}, status=404)

        current_week = _get_current_week(cycle)
        week = int(request.query_params.get("week", current_week))

        entries = (
            TeacherObservationSchedule.objects.filter(cycle=cycle, week=week)
            .select_related("observed_teacher__user", "observer__user", "time_table")
            .order_by("observer__id", "id")
        )

        # Group by observer
        grouped = {}
        for entry in entries:
            obs_id = entry.observer_id
            if obs_id not in grouped:
                grouped[obs_id] = {
                    "observer": _teacher_info(entry.observer),
                    "assignments": [],
                }
            grouped[obs_id]["assignments"].append(_schedule_entry(entry))

        return Response(
            {
                "cycle_id": cycle.id,
                "start_date": cycle.start_date.isoformat(),
                "current_week": current_week,
                "week": week,
                "week_start": (cycle.start_date + timedelta(weeks=week - 1)).isoformat(),
                "observers": list(grouped.values()),
            }
        )
