from rest_framework import generics
from teachers.models import SatisfactionSurvey
from teachers.serializers import SatisfactionSurveyWriteSerializer, SatisfactionSurveyReadSerializer
from rest_framework.response import Response


class SatisfactionSurveyAPIView(generics.ListCreateAPIView):

    def get_serializer_class(self):
        if self.request.method == "GET":
            return SatisfactionSurveyReadSerializer
        return SatisfactionSurveyWriteSerializer

    def get_queryset(self):
        qs = SatisfactionSurvey.objects.select_related(
            "teacher__user",
            "student__user",
            "parent__user",
        )

        teacher = self.request.GET.get("teacher")
        student = self.request.GET.get("student")
        parent = self.request.GET.get("parent")
        year = self.request.GET.get("year")
        month = self.request.GET.get("month")

        if teacher:
            qs = qs.filter(teacher_id=teacher)

        if student:
            qs = qs.filter(student_id=student)

        if parent:
            qs = qs.filter(parent_id=parent)

        if year:
            qs = qs.filter(datetime__year=int(year))

        if month:
            qs = qs.filter(datetime__month=int(month))

        return qs.order_by("-datetime")


class SatisfactionSurveyDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = SatisfactionSurvey.objects.all()

    def get_serializer_class(self):
        if self.request.method == "GET":
            return SatisfactionSurveyReadSerializer
        return SatisfactionSurveyWriteSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"detail": "Deleted"}, status=200)
