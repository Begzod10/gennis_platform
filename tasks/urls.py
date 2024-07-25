from django.urls import path

from tasks.Api.createdelteupdate import TaskCreateView, TaskUpdateView, TaskDestroyView, StudentCallInfoCreateView, \
    StudentCallInfoUpdateView, StudentCallInfoDestroyView
from tasks.Api.get import TaskRetrieveView, TaskListView, CallListView, CallRetrieveView,CreateTask

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

]
