from django.urls import path

from .views import MobileMissionListAPIView, MobileMissionDetailAPIView, MobileMissionStatusAPIView, \
    MobileMissionCommentAPIView, NotificationDetailAPIView, UserNotificationsAPIView

urlpatterns = [
    path(
        "mobile/",
        MobileMissionListAPIView.as_view(),
        name="mobile-mission-list"
    ),
    path(
        "mobile/<int:pk>/",
        MobileMissionDetailAPIView.as_view(),
        name="mobile-mission-detail"
    ),
    path(
        "mobile/<int:pk>/status/",
        MobileMissionStatusAPIView.as_view(),
        name="mobile-mission-status"
    ),
    path(
        "mobile/<int:mission_id>/comments/",
        MobileMissionCommentAPIView.as_view(),
        name="mobile-mission-comments"
    ),
    path(
        "mobile/notifications/",
        UserNotificationsAPIView.as_view(),
        name="mobile-notifications"
    ),
    path(
        "mobile/notifications/<int:pk>/",
        NotificationDetailAPIView.as_view(),
        name="mobile-notification-detail"
    )
]
