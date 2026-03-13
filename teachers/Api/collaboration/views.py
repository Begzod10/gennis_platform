from rest_framework.response import Response
from rest_framework import generics
from django.db.models import Q
from teachers.models import TeamCollaboration
from teachers.serializers import TeamCollaborationReadSerializer, TeamCollaborationWriteSerializer


class TeamCollaborationAPIView(generics.ListCreateAPIView):

    def get_serializer_class(self):
        if self.request.method == "GET":
            return TeamCollaborationReadSerializer
        return TeamCollaborationWriteSerializer

    def get_queryset(self):

        qs = TeamCollaboration.objects.select_related(
            "teacher__user",
            "user"
        )

        teacher = self.request.GET.get("teacher")
        user = self.request.GET.get("user")
        branch = self.request.GET.get("branch")
        year = self.request.GET.get("year")
        month = self.request.GET.get("month")

        if teacher:
            qs = qs.filter(teacher_id=teacher)

        if user:
            qs = qs.filter(user_id=user)

        if branch:
            qs = qs.filter(teacher__user__branch_id=branch)

        if year:
            qs = qs.filter(datetime__year=int(year))

        if month:
            qs = qs.filter(datetime__month=int(month))

        return qs.order_by("-datetime")


class TeamCollaborationDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = TeamCollaboration.objects.all()

    def get_serializer_class(self):
        if self.request.method == "GET":
            return TeamCollaborationReadSerializer
        return TeamCollaborationWriteSerializer
