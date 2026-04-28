from rest_framework.response import Response
from rest_framework import generics
from teachers.models import ProfessionalConduct
from teachers.serializers import ConductReadSerializer, ConductWriteSerializer


class ConductAPIView(generics.ListCreateAPIView):

    def get_serializer_class(self):
        if self.request.method == "GET":
            return ConductReadSerializer
        return ConductWriteSerializer

    def get_queryset(self):

        qs = ProfessionalConduct.objects.select_related(
            "teacher__user",
            "created_by"
        )

        teacher = self.request.GET.get("teacher")
        year = self.request.GET.get("year")
        month = self.request.GET.get("month")

        if teacher:
            qs = qs.filter(teacher_id=teacher)

        if year:
            qs = qs.filter(datetime__year=int(year))

        if month:
            qs = qs.filter(datetime__month=int(month))

        return qs

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class ConductDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ProfessionalConduct.objects.select_related(
        "teacher__user",
        "created_by"
    )

    def get_serializer_class(self):
        if self.request.method == "GET":
            return ConductReadSerializer
        return ConductWriteSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"detail": "Deleted"}, status=200)
