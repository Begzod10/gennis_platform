from django.urls import path

from tasks.Api.createdelteupdate import TaskCreateView, TaskUpdateView, TaskDestroyView
from tasks.Api.get import TaskRetrieveView

urlpatterns = [
    path('task_create/', TaskCreateView.as_view(), name='task-create'),
    path('task_update/', TaskUpdateView.as_view(), name='task-update'),
    path('task_delete/', TaskDestroyView.as_view(), name='task-destroy'),
    # path('call_info/', StudentCallinfoCreateView.as_view(), name='call-list-create'),
    path('tasks/<int:pk>/', TaskRetrieveView.as_view(), name='task-detail'),
]
