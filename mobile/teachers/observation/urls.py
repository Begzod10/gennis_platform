from django.urls import path

from .views import ObservationInfoList, ObservationOptionsList, TeacherObserveView, TeacherObserveGroupView
from .schedule_views import (
    MobileTeacherScheduleView,
    MobileTeacherFullScheduleView,
    MobileCompleteObservationView,
    MobileCurrentWeekScheduleView,
)

urlpatterns = [
    path('observation_info_list/', ObservationInfoList.as_view(), name='observation-info-list'),
    path('observation_options/', ObservationOptionsList.as_view(), name='observation-options-list'),
    path('teacher_observe/', TeacherObserveView.as_view(), name='teacher-observe'),
    path('teacher_observe/<int:group_id>', TeacherObserveView.as_view(), name='teacher-observe'),
    path('teacher_options/', TeacherObserveGroupView.as_view(), name='teacher-options'),

    # Observation schedule
    path('schedule/', MobileTeacherScheduleView.as_view(), name='mobile-obs-schedule'),
    path('schedule/current_week/', MobileCurrentWeekScheduleView.as_view(), name='mobile-obs-schedule-current-week'),
    path('schedule/all/', MobileTeacherFullScheduleView.as_view(), name='mobile-obs-schedule-all'),
    path('schedule/<int:pk>/complete/', MobileCompleteObservationView.as_view(), name='mobile-obs-complete'),
]


