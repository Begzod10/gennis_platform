from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiParameter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.shortcuts import get_object_or_404

from lesson_plan.models import LessonPlanFile
from teachers.models import Teacher
from terms.models import Term


class LessonPlanFileUploadView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request={"multipart/form-data": {"type": "object", "properties": {
            "teacher_id": {"type": "integer"},
            "term_id": {"type": "integer"},
            "file": {"type": "string", "format": "binary"},
        }, "required": ["teacher_id", "term_id", "file"]}},
        responses={201: dict, 200: dict},
        examples=[
            OpenApiExample("Response", value={
                "id": 3, "teacher_id": 5, "term_id": 2,
                "status": "pending", "detail": "File uploaded. AI review started."
            }, response_only=True),
        ],
        summary="Upload lesson plan file for AI review (admin)",
        tags=["lesson-plan-file"],
    )
    def post(self, request):
        teacher_id = request.data.get("teacher_id")
        term_id = request.data.get("term_id")
        file = request.FILES.get("file")

        if not teacher_id or not term_id or not file:
            return Response({"detail": "teacher_id, term_id and file are required."}, status=400)

        allowed = {".txt", ".pdf", ".docx", ".xlsx"}
        
        ext = "." + file.name.rsplit(".", 1)[-1].lower() if "." in file.name else ""
        if ext not in allowed:
            return Response({"detail": f"Unsupported format. Allowed: {', '.join(allowed)}"}, status=400)

        teacher = get_object_or_404(Teacher, id=teacher_id)
        term = get_object_or_404(Term, id=term_id)

        lp_file, created = LessonPlanFile.objects.update_or_create(
            teacher=teacher,
            term=term,
            defaults={
                "file": file,
                "status": LessonPlanFile.Status.PENDING,
                "score": None,
                "feedback": None,
                "reviewed_at": None,
            },
        )

        from lesson_plan.tasks import review_lesson_plan_file
        review_lesson_plan_file.delay(lp_file.id)

        return Response(
            {
                "id": lp_file.id,
                "teacher_id": teacher.id,
                "term_id": term.id,
                "status": lp_file.status,
                "detail": "File uploaded. AI review started.",
            },
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )


class LessonPlanFileDetailView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: dict},
        examples=[
            OpenApiExample("Response", value={
                "id": 3,
                "teacher": {"id": 5, "name": "Ali", "surname": "Valiev"},
                "term": {"id": 2, "quarter": 2, "academic_year": "2025-2026"},
                "file": "/media/lesson_plan_files/2026/04/plan.pdf",
                "status": "done", "score": 82,
                "feedback": "Dars rejasi yaxshi tuzilgan. Maqsad va vazifalar aniq.",
                "uploaded_at": "2026-04-15T10:00:00Z", "reviewed_at": "2026-04-15T10:02:31Z"
            }, response_only=True),
        ],
        summary="Get AI review result for a lesson plan file",
        tags=["lesson-plan-file"],
    )
    def get(self, request, pk):
        lp_file = get_object_or_404(
            LessonPlanFile.objects.select_related("teacher__user", "term"),
            pk=pk,
        )
        return Response(_serialize(lp_file))


class LessonPlanFileListView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        parameters=[
            OpenApiParameter("teacher_id", int, description="Filter by teacher ID"),
            OpenApiParameter("term_id", int, description="Filter by term ID"),
        ],
        responses={200: dict},
        examples=[
            OpenApiExample("Response", value=[
                {"id": 3, "teacher": {"id": 5, "name": "Ali", "surname": "Valiev"},
                 "term": {"id": 2, "quarter": 2, "academic_year": "2025-2026"},
                 "file": "/media/lesson_plan_files/2026/04/plan.pdf",
                 "status": "done", "score": 82,
                 "feedback": "Dars rejasi yaxshi tuzilgan.",
                 "uploaded_at": "2026-04-15T10:00:00Z", "reviewed_at": "2026-04-15T10:02:31Z"},
            ], response_only=True),
        ],
        summary="List lesson plan files (filter by teacher/term)",
        tags=["lesson-plan-file"],
    )
    def get(self, request):
        qs = LessonPlanFile.objects.select_related("teacher__user", "term")

        teacher_id = request.query_params.get("teacher_id")
        term_id = request.query_params.get("term_id")

        if teacher_id:
            qs = qs.filter(teacher_id=teacher_id)
        if term_id:
            qs = qs.filter(term_id=term_id)

        return Response([_serialize(f) for f in qs])


class LessonPlanFileRateView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request={"application/json": {"type": "object", "properties": {
            "rating": {"type": "integer", "minimum": 0, "maximum": 5},
        }, "required": ["rating"]}},
        responses={200: dict},
        examples=[
            OpenApiExample("Request", value={"rating": 4}, request_only=True),
            OpenApiExample("Response", value={"id": 3, "rating": 4, "detail": "Rating saved."}, response_only=True),
        ],
        summary="Set manual rating (0–5) for a lesson plan file",
        tags=["lesson-plan-file"],
    )
    def patch(self, request, pk):
        lp_file = get_object_or_404(LessonPlanFile, pk=pk)
        rating = request.data.get("rating")

        if rating is None:
            return Response({"detail": "rating is required."}, status=400)

        try:
            rating = int(rating)
        except (TypeError, ValueError):
            return Response({"detail": "rating must be an integer."}, status=400)

        if not (0 <= rating <= 5):
            return Response({"detail": "rating must be between 0 and 5."}, status=400)

        lp_file.rating = rating
        lp_file.save(update_fields=["rating"])

        return Response({"id": lp_file.id, "rating": lp_file.rating, "detail": "Rating saved."})


def _serialize(lp_file: LessonPlanFile) -> dict:
    return {
        "id": lp_file.id,
        "teacher": {
            "id": lp_file.teacher_id,
            "name": lp_file.teacher.user.name if lp_file.teacher.user else "",
            "surname": lp_file.teacher.user.surname if lp_file.teacher.user else "",
        },
        "term": {
            "id": lp_file.term_id,
            "quarter": lp_file.term.quarter,
            "academic_year": lp_file.term.academic_year,
        },
        "file": lp_file.file.url if lp_file.file else None,
        "status": lp_file.status,
        "score": lp_file.score,
        "rating": lp_file.rating,
        "feedback": lp_file.feedback,
        "uploaded_at": lp_file.uploaded_at,
        "reviewed_at": lp_file.reviewed_at,
    }
