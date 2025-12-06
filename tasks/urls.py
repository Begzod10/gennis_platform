from django.urls import path

from tasks.Api.createdelteupdate import TaskCreateView, TaskUpdateView, TaskDestroyView, StudentCallInfoCreateView, \
    StudentCallInfoUpdateView, StudentCallInfoDestroyView
from tasks.Api.get import TaskRetrieveView, TaskListView, CallListView, CallRetrieveView, CreateTask
from tasks.Api.missions.views import MissionDetailAPIView, MissionListCreateAPIView
from tasks.Api.missions.subtasks.views import SubtaskListCreateAPIView, SubtaskDetailAPIView
from tasks.Api.missions.comment.views import CommentDetailAPIView, CommentListCreateAPIView
from tasks.Api.missions.attachment.views import AttachmentDetailAPIView, AttachmentListCreateAPIView
from tasks.Api.missions.proof.views import ProofDetailAPIView, ProofListCreateAPIView
from tasks.Api.missions.tag.views import TagDetailAPIView, TagListCreateAPIView
from tasks.Api.missions.notification.views import UserNotificationsAPIView, NotificationDetailAPIView

urlpatterns = [
    path('task_create/', TaskCreateView.as_view(), name='task-create'),
    path('task_update/<int:pk>/', TaskUpdateView.as_view(), name='task-update'),
    path('task_delete/<int:pk>/', TaskDestroyView.as_view(), name='task-destroy'),
    path('tasks/', TaskListView.as_view(), name='task-all'),
    path('tasks/<int:pk>/', TaskRetrieveView.as_view(), name='task-detail'),
    path('call_info_create/', StudentCallInfoCreateView.as_view(), name='call-create'),
    path('call_info_update/', StudentCallInfoUpdateView.as_view(), name='call-update'),
    path('call_info_delete/', StudentCallInfoDestroyView.as_view(), name='call-delete'),
    path('call_info/', CallListView.as_view(), name='call-all'),
    path('call_info/<int:pk>/', CallRetrieveView.as_view(), name='call-detail'),
    path('dailiy_task_create/', CreateTask.as_view(), name='task-daily-create'),

    path("missions/", MissionListCreateAPIView.as_view()),
    path("missions/<int:pk>/", MissionDetailAPIView.as_view()),

    path("subtasks/", SubtaskListCreateAPIView.as_view()),
    path("subtasks/<int:pk>/", SubtaskDetailAPIView.as_view()),

    path("comments/", CommentListCreateAPIView.as_view()),
    path("comments/<int:pk>/", CommentDetailAPIView.as_view()),

    path("attachments/", AttachmentListCreateAPIView.as_view()),
    path("attachments/<int:pk>/", AttachmentDetailAPIView.as_view()),

    path("proofs/", ProofListCreateAPIView.as_view()),
    path("proofs/<int:pk>/", ProofDetailAPIView.as_view()),

    path("tags/", TagListCreateAPIView.as_view()),
    path("tags/<int:pk>/", TagDetailAPIView.as_view()),

    path("notifications/", UserNotificationsAPIView.as_view()),
    path("notifications/<int:pk>/", NotificationDetailAPIView.as_view()),

]
