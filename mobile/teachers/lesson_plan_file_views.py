from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiParameter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from lesson_plan.models import LessonPlanFile
from teachers.models import Teacher
from terms.models import Term


class MobileLessonPlanFileUploadView(APIView):
    """
    POST /mobile/teachers/lesson-plan/file/upload/
    Form-data: term_id (int), file (.txt / .pdf / .docx)

    Teacher uploads their lesson plan file for a term.
    AI review starts automatically in the background.
    One file per teacher per term — re-uploading replaces the previous one.
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request={"multipart/form-data": {"type": "object", "properties": {
            "term_id": {"type": "integer"},
            "group_id": {"type": "integer", "nullable": True},
            "flow_id": {"type": "integer", "nullable": True},
            "file": {"type": "string", "format": "binary"},
        }}},
        responses={201: dict, 200: dict},
        examples=[
            OpenApiExample(
                "Success response",
                value={
                    "id": 3,
                    "term_id": 2,
                    "group_id": 1,
                    "flow_id": None,
                    "status": "pending",
                    "detail": "File uploaded. AI review started."
                },
                response_only=True,
            )
        ],
        summary="Upload lesson plan file for AI review",
        tags=["mobile-lesson-plan"],
    )
    def post(self, request):
        teacher = Teacher.objects.filter(user=request.user, deleted=False).first()
        if not teacher:
            return Response({"detail": "Teacher not found."}, status=404)

        term_id = request.data.get("term_id")
        group_id = request.data.get("group_id")
        flow_id = request.data.get("flow_id")
        file = request.FILES.get("file")

        if not term_id or not file:
            return Response({"detail": "term_id and file are required."}, status=400)

        allowed = {".txt", ".pdf", ".docx", ".xlsx"}
        ext = "." + file.name.rsplit(".", 1)[-1].lower() if "." in file.name else ""
        if ext not in allowed:
            return Response(
                {"detail": f"Unsupported format. Allowed: {', '.join(allowed)}"},
                status=400,
            )

        try:
            term = Term.objects.get(id=term_id)
        except Term.DoesNotExist:
            return Response({"detail": "Term not found."}, status=404)
            
        from group.models import Group
        from flows.models import Flow
        group = None
        if group_id:
            try:
                group = Group.objects.get(id=group_id)
            except Group.DoesNotExist:
                return Response({"detail": "Group not found."}, status=404)
                
        flow = None
        if flow_id:
            try:
                flow = Flow.objects.get(id=flow_id)
            except Flow.DoesNotExist:
                return Response({"detail": "Flow not found."}, status=404)

        lp_file, created = LessonPlanFile.objects.update_or_create(
            teacher=teacher,
            term=term,
            group=group,
            flow=flow,
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
                "term_id": term.id,
                "group_id": group.id if group else None,
                "flow_id": flow.id if flow else None,
                "status": lp_file.status,
                "detail": "File uploaded. AI review started.",
            },
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )


class MobileLessonPlanFileStatusView(APIView):
    """
    GET /mobile/teachers/lesson-plan/file/<id>/

    Returns the AI review status, score, and feedback for a specific file.
    Teacher can only view their own files.
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: dict},
        examples=[
            OpenApiExample(
                "Pending",
                value={
                    "id": 3,
                    "term": {"id": 2, "quarter": 2, "academic_year": "2025-2026"},
                    "file": "/media/lesson_plan_files/2026/04/plan.pdf",
                    "status": "checking",
                    "score": None,
                    "feedback": None,
                    "uploaded_at": "2026-04-15T10:00:00Z",
                    "reviewed_at": None
                },
                response_only=True,
            ),
            OpenApiExample(
                "Done",
                value={
                    "id": 3,
                    "term": {"id": 2, "quarter": 2, "academic_year": "2025-2026"},
                    "file": "/media/lesson_plan_files/2026/04/plan.pdf",
                    "status": "done",
                    "score": 82,
                    "rating": 4,
                    "feedback": "Dars rejasi yaxshi tuzilgan. Maqsad va vazifalar aniq ko'rsatilgan. Baholash mezonlari to'liq emas.",
                    "uploaded_at": "2026-04-15T10:00:00Z",
                    "reviewed_at": "2026-04-15T10:02:31Z"
                },
                response_only=True,
            ),
        ],
        summary="Get AI review result for a lesson plan file",
        tags=["mobile-lesson-plan"],
    )
    def get(self, request, pk):
        teacher = Teacher.objects.filter(user=request.user, deleted=False).first()
        if not teacher:
            return Response({"detail": "Teacher not found."}, status=404)

        try:
            lp_file = LessonPlanFile.objects.select_related("term").get(pk=pk, teacher=teacher)
        except LessonPlanFile.DoesNotExist:
            return Response({"detail": "File not found."}, status=404)

        return Response(_serialize(lp_file))


class MobileLessonPlanFileListView(APIView):
    """
    GET /mobile/teachers/lesson-plan/file/

    Returns all lesson plan files uploaded by the authenticated teacher.
    Optional filter: ?term_id=X
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        parameters=[
            OpenApiParameter("term_id", int, description="Filter by term ID"),
            OpenApiParameter("group_id", int, description="Filter by group ID"),
            OpenApiParameter("flow_id", int, description="Filter by flow ID"),
        ],
        responses={200: dict},
        examples=[
            OpenApiExample(
                "List",
                value=[
                    {
                        "id": 3,
                        "term": {"id": 2, "quarter": 2, "academic_year": "2025-2026"},
                        "file": "/media/lesson_plan_files/2026/04/plan.pdf",
                        "status": "done",
                        "score": 82,
                        "feedback": "Dars rejasi yaxshi tuzilgan...",
                        "uploaded_at": "2026-04-15T10:00:00Z",
                        "reviewed_at": "2026-04-15T10:02:31Z"
                    }
                ],
                response_only=True,
            )
        ],
        summary="List teacher's lesson plan files",
        tags=["mobile-lesson-plan"],
    )
    def get(self, request):
        teacher = Teacher.objects.filter(user=request.user, deleted=False).first()
        if not teacher:
            return Response({"detail": "Teacher not found."}, status=404)

        qs = LessonPlanFile.objects.filter(teacher=teacher).select_related("term")
        term_id = request.query_params.get("term_id")
        group_id = request.query_params.get("group_id")
        flow_id = request.query_params.get("flow_id")
        
        if term_id:
            qs = qs.filter(term_id=term_id)
        if group_id:
            qs = qs.filter(group_id=group_id)
        if flow_id:
            qs = qs.filter(flow_id=flow_id)

        return Response([_serialize(f) for f in qs])


def _serialize(lp_file: LessonPlanFile) -> dict:
    return {
        "id": lp_file.id,
        "term": {
            "id": lp_file.term_id,
            "quarter": lp_file.term.quarter,
            "academic_year": lp_file.term.academic_year,
        },
        "group": {
            "id": lp_file.group_id,
            "name": lp_file.group.name if lp_file.group else None,
        } if lp_file.group_id else None,
        "flow": {
            "id": lp_file.flow_id,
            "name": lp_file.flow.name if lp_file.flow else None,
        } if lp_file.flow_id else None,
        "file": lp_file.file.url if lp_file.file else None,
        "status": lp_file.status,
        "score": lp_file.score,
        "rating": lp_file.rating,
        "feedback": lp_file.feedback,
        "uploaded_at": lp_file.uploaded_at,
        "reviewed_at": lp_file.reviewed_at,
    }
