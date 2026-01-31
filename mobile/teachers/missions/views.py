from rest_framework.generics import ListAPIView, RetrieveAPIView, UpdateAPIView
from mobile.teachers.missions.serializers import MobileMissionSerializer, MobileMissionDetailSerializer, \
    MobileMissionStatusSerializer, MobileMissionCommentCreateSerializer, MobileMissionCommentSerializer
from user.models import CustomUser
from tasks.serializers import NotificationSerializer
from tasks.models import Mission, Notification, MissionComment
from django.utils import timezone
from tasks.signals import send_notification
from datetime import timedelta, date
from django.db import models
from rest_framework import generics
from django.shortcuts import get_object_or_404


class MobileMissionListAPIView(ListAPIView):
    serializer_class = MobileMissionSerializer

    def get_queryset(self):
        user_id = int(self.request.query_params.get("user_id"))
        print(user_id)
        user = CustomUser.objects.get(pk=user_id)
        print(user)
        qs = (
            Mission.objects
            .filter(executor=user)
            .select_related("creator", "executor", "reviewer", "redirected_by")
            .prefetch_related("tags")
            .order_by("deadline")
        )

        # 🔹 query param: status
        status_param = self.request.query_params.get("status")
        if status_param:
            qs = qs.filter(status=status_param)

        return qs


class MobileMissionDetailAPIView(RetrieveAPIView):
    serializer_class = MobileMissionDetailSerializer

    def get_queryset(self):
        return (
            Mission.objects
            .select_related("creator", "executor", "reviewer", "redirected_by")
            .prefetch_related("tags", "comments", "attachments", "proofs", "subtasks")
        )


class MobileMissionStatusAPIView(UpdateAPIView):
    serializer_class = MobileMissionStatusSerializer

    def get_queryset(self):
        return Mission.objects.filter(executor=self.request.user)

    def perform_update(self, serializer):
        mission = serializer.save()

        # finish + score
        if mission.status == "completed" and not mission.finish_date:
            mission.finish_date = timezone.now().date()
            mission.calculate_delay_days()
            mission.final_sc = mission.final_score()
            mission.save()

        # 🔔 notification
        send_notification(
            user=mission.creator,
            mission=mission,
            message=f"Task yakunlandi: {mission.title}",
            role="creator"
        )


class MobileMissionCommentAPIView(generics.ListCreateAPIView):

    def get_queryset(self):
        mission_id = int(self.kwargs["mission_id"])
        user_id = int(self.request.query_params.get("user"))
        user = CustomUser.objects.get(pk=user_id)

        return MissionComment.objects.filter(
            mission_id=mission_id,
            mission__executor=user
        ).select_related("user")

    def get_serializer_class(self):
        if self.request.method == "POST":
            return MobileMissionCommentCreateSerializer
        return MobileMissionCommentSerializer

    def perform_create(self, serializer):
        mission_id = self.kwargs["mission_id"]
        user_id = int(self.request.query_params.get("user"))
        user = CustomUser.objects.get(pk=user_id)
        mission = get_object_or_404(
            Mission,
            id=mission_id,
            executor=user
        )

        comment = serializer.save(
            mission=mission,
            user=user
        )

        # 🔔 NOTIFICATION (creator ga)
        send_notification(
            user=mission.creator,
            mission=mission,
            message=f"{user.get_full_name()} taskga comment yozdi"
        )


class UserNotificationsAPIView(generics.ListAPIView):
    serializer_class = NotificationSerializer

    def get_queryset(self):
        role = "executor"
        user_id = int(self.request.query_params.get("user_id"))

        today = date.today()
        if role == "executor" and user_id:
            missions = Mission.objects.filter(
                executor_id=user_id,
                status__in=["not_started", "in_progress"]
            )

            for mission in missions:
                # 1 kun qolgan xabar
                if mission.deadline == today + timedelta(days=1):
                    if not Notification.objects.filter(
                            user_id=user_id,
                            mission=mission,
                            message__icontains="deadline yaqin",
                            role="executor"
                    ).exists():
                        Notification.objects.create(
                            user_id=user_id,
                            mission=mission,
                            message=f"Vazifa '{mission.title}' deadline yaqin: {mission.deadline}",
                            role="executor",
                            deadline=mission.deadline
                        )

                # Deadline o'tib ketgan xabar
                elif mission.deadline < today:
                    if not Notification.objects.filter(
                            user_id=user_id,
                            mission=mission,
                            message__icontains="o‘tib ketdi",
                            role="executor"
                    ).exists():
                        Notification.objects.create(
                            user_id=user_id,
                            mission=mission,
                            message=f"Vazifa '{mission.title}' deadline o‘tib ketdi: {mission.deadline}",
                            role="executor",
                            deadline=mission.deadline
                        )

        qs = Notification.objects.all()

        if user_id:
            qs = qs.filter(user_id=user_id)
        if role:
            qs = qs.filter(role=role)

        qs = qs.filter(
            models.Q(is_read=False) | models.Q(mission__deadline__gte=today)
        )

        return qs.order_by("-created_at")


class NotificationDetailAPIView(generics.RetrieveUpdateAPIView):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)
