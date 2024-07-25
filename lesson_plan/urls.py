from django.urls import path

from lesson_plan.Api.get import LessonPlanListView, GetLessonPlanView
from lesson_plan.Api.update import ChangeLessonPlanView

urlpatterns = [
    path('change_lesson_plan/<int:plan_id>/', ChangeLessonPlanView.as_view(), name='change_lesson_plan'),
    path('lesson_plan_list/<int:group_id>/', LessonPlanListView.as_view(), name='lesson_plan_list'),
    path('lesson_plan_list/<int:group_id>/<str:date>/', LessonPlanListView.as_view(),
         name='lesson_plan_list_with_date'),
    path('get_lesson_plan/', GetLessonPlanView.as_view(), name='get_lesson_plan'),
]
