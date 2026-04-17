from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiParameter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from teachers.models import Teacher
from observation.models import TeacherObservationDay
from lesson_plan.models import LessonPlanFile


class TeacherStatsView(APIView):
    """
    GET observation/teacher_stats/

    Returns observation ratings and lesson plan file data for each teacher.
    Optional filters: ?branch_id=X  ?term_id=X
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        parameters=[
            OpenApiParameter("branch_id", int, description="Filter teachers by branch ID"),
            OpenApiParameter("term_id", int, description="Filter lesson plan files by term ID"),
        ],
        responses={200: dict},
        examples=[
            OpenApiExample(
                "Response",
                value=[
                    {
                        "teacher": {"id": 1, "name": "Ali", "surname": "Valiev"},
                        "observation": {
                            "count": 3,
                            "average": 85,
                            "days": [
                                {"id": 1, "date": "2026-04-10", "average": 80, "observer": "Shodmon Toshev"},
                                {"id": 2, "date": "2026-04-14", "average": 90, "observer": "Zulfiya Rahimova"},
                            ]
                        },
                        "lesson_plan": {
                            "id": 2,
                            "status": "done",
                            "score": 82,
                            "rating": 4,
                            "feedback": "Dars rejasi yaxshi tuzilgan.",
                            "uploaded_at": "2026-04-15T10:00:00Z",
                            "reviewed_at": "2026-04-15T10:02:31Z"
                        }
                    }
                ],
                response_only=True,
            )
        ],
        summary="Teacher statistics: observation ratings + lesson plan file",
        tags=["statistics"],
    )
    def get(self, request):
        branch_id = request.query_params.get("branch_id")
        term_id = request.query_params.get("term_id")

        teacher_qs = Teacher.objects.select_related("user").filter(deleted=False)
        if branch_id:
            teacher_qs = teacher_qs.filter(branches__id=branch_id)

        # Prefetch observation days for all these teachers at once
        teacher_ids = list(teacher_qs.values_list("id", flat=True))

        obs_days = (
            TeacherObservationDay.objects
            .filter(teacher_id__in=teacher_ids)
            .select_related("user")
        )
        # Group by observed teacher
        obs_map: dict[int, list] = {}
        for day in obs_days:
            obs_map.setdefault(day.teacher_id, []).append(day)

        # Lesson plan files
        lp_qs = LessonPlanFile.objects.filter(teacher_id__in=teacher_ids)
        if term_id:
            lp_qs = lp_qs.filter(term_id=term_id)
        lp_map = {lp.teacher_id: lp for lp in lp_qs}

        result = []
        for teacher in teacher_qs:
            days = obs_map.get(teacher.id, [])
            avg = round(sum(d.average for d in days) / len(days)) if days else None
            lp = lp_map.get(teacher.id)

            result.append({
                "teacher": {
                    "id": teacher.id,
                    "name": teacher.user.name if teacher.user else "",
                    "surname": teacher.user.surname if teacher.user else "",
                },
                "observation": {
                    "count": len(days),
                    "average": avg,
                    "days": [
                        {
                            "id": d.id,
                            "date": d.date,
                            "average": d.average,
                            "observer": f"{d.user.name} {d.user.surname}" if d.user else "",
                        }
                        for d in days
                    ],
                },
                "lesson_plan": {
                    "id": lp.id,
                    "status": lp.status,
                    "score": lp.score,
                    "rating": lp.rating,
                    "feedback": lp.feedback,
                    "uploaded_at": lp.uploaded_at,
                    "reviewed_at": lp.reviewed_at,
                } if lp else None,
            })

        return Response(result)
