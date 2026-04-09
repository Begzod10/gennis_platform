from datetime import date, timedelta
from rest_framework import generics
from django.db import models
from tasks.models import Notification
from tasks.serializers import NotificationSerializer
from tasks.models import Mission


class UserNotificationsAPIView(generics.ListAPIView):
    serializer_class = NotificationSerializer

    def get_queryset(self):
        role = self.request.query_params.get("role")
        user_id = self.request.query_params.get("user_id")

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
