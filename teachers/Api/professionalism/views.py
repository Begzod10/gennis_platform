from rest_framework.response import Response
from rest_framework import generics
from teachers.models import TeacherProfessionalism
from teachers.serializers import TeacherProfessionalismReadSerializer, TeacherProfessionalismWriteSerializer


class TeacherProfessionalismAPIView(generics.ListCreateAPIView):

    def get_serializer_class(self):
        if self.request.method == "GET":
            return TeacherProfessionalismReadSerializer
        return TeacherProfessionalismWriteSerializer

    def get_queryset(self):
        qs = TeacherProfessionalism.objects.select_related(
            "teacher__user",
            "user"
        )

        teacher = self.request.GET.get("teacher")
        user = self.request.GET.get("user")
        year = self.request.GET.get("year")
        month = self.request.GET.get("month")

        if teacher:
            qs = qs.filter(teacher_id=teacher)

        if user:
            qs = qs.filter(user_id=user)

        if year:
            qs = qs.filter(datetime__year=int(year))

        if month:
            qs = qs.filter(datetime__month=int(month))

        return qs


class TeacherProfessionalismDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = TeacherProfessionalism.objects.all()

    def get_serializer_class(self):
        if self.request.method == "GET":
            return TeacherProfessionalismReadSerializer
        return TeacherProfessionalismWriteSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"detail": "Deleted"}, status=200)
