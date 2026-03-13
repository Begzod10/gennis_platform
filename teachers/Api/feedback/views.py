from rest_framework.response import Response
from rest_framework import generics
from django.db.models import Q
from teachers.models import ResponsivenessFeedback
from teachers.serializers import ResponsivenessReadSerializer, ResponsivenessWriteSerializer


class ResponsivenessAPIView(generics.ListCreateAPIView):

    def get_serializer_class(self):
        if self.request.method == "GET":
            return ResponsivenessReadSerializer
        return ResponsivenessWriteSerializer

    def get_queryset(self):

        qs = ResponsivenessFeedback.objects.select_related(
            "teacher__user",
            "user"
        )

        teacher = self.request.GET.get("teacher")
        user = self.request.GET.get("user")
        year = self.request.GET.get("year")
        month = self.request.GET.get("month")
        branch = self.request.GET.get("branch")

        if teacher:
            qs = qs.filter(teacher_id=teacher)

        if branch:
            qs = qs.filter(teacher__user__branch_id=branch)

        if user:
            qs = qs.filter(user_id=user)

        if year:
            qs = qs.filter(datetime__year=int(year))

        if month:
            qs = qs.filter(datetime__month=int(month))

        return qs.order_by("-datetime")


class ResponsivenessDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ResponsivenessFeedback.objects.all()

    def get_serializer_class(self):
        if self.request.method == "GET":
            return ResponsivenessReadSerializer
        return ResponsivenessWriteSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"detail": "Deleted"}, status=200)
