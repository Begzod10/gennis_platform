from django.urls import path
from .views import TaskListCreateView, TaskRetrieveUpdateDestroyView,StudentCallinfoCreateView

urlpatterns = [
    path('tasks/', TaskListCreateView.as_view(), name='task-list-create'),
    path('call_info/', StudentCallinfoCreateView.as_view(), name='call-list-create'),
    path('tasks/<int:pk>/', TaskRetrieveUpdateDestroyView.as_view(), name='task-detail'),
]
