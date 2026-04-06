from django.urls import path

from tasks.Api.createdelteupdate import TaskCreateView, TaskUpdateView, TaskDestroyView, StudentCallInfoCreateView, \
    StudentCallInfoUpdateView, StudentCallInfoDestroyView
from tasks.Api.get import TaskRetrieveView, TaskListView, CallListView, CallRetrieveView, CreateTask
from tasks.Api.missions.views import MissionDetailAPIView, MissionListCreateAPIView
from tasks.admin.tasks import DebtorsAPIView, CreateCallLogAPIView, TodayCallsAPIView

urlpatterns = [
    path("debtors/", DebtorsAPIView.as_view()),
    path("callog/", CreateCallLogAPIView.as_view()),
    path("today-calls/", TodayCallsAPIView.as_view()),
]
