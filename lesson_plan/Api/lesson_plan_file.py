from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.shortcuts import get_object_or_404

from lesson_plan.models import LessonPlanFile
from teachers.models import Teacher
from terms.models import Term


class LessonPlanFileUploadView(APIView):
    """
    POST /lesson_plan/file/upload/
    Form-data: teacher_id, term_id, file

    Upload a lesson plan file for a term. Triggers AI review task automatically.
    One file per teacher per term (updates if already exists).
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        teacher_id = request.data.get("teacher_id")
        term_id = request.data.get("term_id")
        file = request.FILES.get("file")

        if not teacher_id or not term_id or not file:
            return Response({"detail": "teacher_id, term_id and file are required."}, status=400)

        allowed = {".txt", ".pdf", ".docx"}
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
    """
    GET /lesson_plan/file/<id>/

    Returns the current review status, score, and feedback for a file.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        lp_file = get_object_or_404(
            LessonPlanFile.objects.select_related("teacher__user", "term"),
            pk=pk,
        )
        return Response(_serialize(lp_file))


class LessonPlanFileListView(APIView):
    """
    GET /lesson_plan/file/?teacher_id=X&term_id=X

    List lesson plan files. Filters by teacher_id and/or term_id.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = LessonPlanFile.objects.select_related("teacher__user", "term")

        teacher_id = request.query_params.get("teacher_id")
        term_id = request.query_params.get("term_id")

        if teacher_id:
            qs = qs.filter(teacher_id=teacher_id)
        if term_id:
            qs = qs.filter(term_id=term_id)

        return Response([_serialize(f) for f in qs])


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
        "feedback": lp_file.feedback,
        "uploaded_at": lp_file.uploaded_at,
        "reviewed_at": lp_file.reviewed_at,
    }
