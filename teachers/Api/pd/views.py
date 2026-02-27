from rest_framework.response import Response
from rest_framework import generics
from teachers.models import PDParticipant, ProfessionalDevelopment
from teachers.serializers import PDReadSerializer, PDWriteSerializer


class PDAPIView(generics.ListCreateAPIView):

    def get_serializer_class(self):
        if self.request.method == "GET":
            return PDReadSerializer
        return PDWriteSerializer

    def get_queryset(self):
        qs = (
            ProfessionalDevelopment.objects
            .select_related("speaker__user", "created_by")
            .prefetch_related("participants__teacher__user")
        )

        speaker = self.request.GET.get("speaker")
        teacher = self.request.GET.get("teacher")
        year = self.request.GET.get("year")
        month = self.request.GET.get("month")

        if speaker:
            qs = qs.filter(speaker_id=speaker)

        if teacher:
            qs = qs.filter(participants__teacher_id=teacher)

        if year:
            qs = qs.filter(datetime__year=int(year))

        if month:
            qs = qs.filter(datetime__month=int(month))

        return qs.distinct()


class PDDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ProfessionalDevelopment.objects.all()

    def get_serializer_class(self):
        if self.request.method == "GET":
            return PDReadSerializer
        return PDWriteSerializer


class PDParticipantUpdateAPIView(generics.UpdateAPIView):
    queryset = PDParticipant.objects.all()
    fields = ["status"]

    def perform_update(self, serializer):
        serializer.save(marked_by=self.request.user)
