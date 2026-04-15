from django.urls import path

from lesson_plan.Api.get import LessonPlanListView, GetLessonPlanView
from lesson_plan.Api.update import ChangeLessonPlanView
from lesson_plan.Api.lesson_plan_file import (
    LessonPlanFileUploadView,
    LessonPlanFileDetailView,
    LessonPlanFileListView,
)

urlpatterns = [
    path('change_lesson_plan/<int:pk>/', ChangeLessonPlanView.as_view(), name='change_lesson_plan'),
    path('lesson_plan_list/<int:group_id>/', LessonPlanListView.as_view(), name='lesson_plan_list'),
    path('lesson_plan_list/<int:group_id>/<str:date>/', LessonPlanListView.as_view(),
         name='lesson_plan_list_with_date'),
    path('get_lesson_plan/', GetLessonPlanView.as_view(), name='get_lesson_plan'),

    # Lesson plan file upload + AI review
    path('file/upload/', LessonPlanFileUploadView.as_view(), name='lesson-plan-file-upload'),
    path('file/<int:pk>/', LessonPlanFileDetailView.as_view(), name='lesson-plan-file-detail'),
    path('file/', LessonPlanFileListView.as_view(), name='lesson-plan-file-list'),
]
