from django.urls import path

from .views import ObservationInfoList, ObservationOptionsList, TeacherObserveView

urlpatterns = [
    path('observation_info_list/', ObservationInfoList.as_view(), name='observation-info-list'),
    path('observation_options/', ObservationOptionsList.as_view(), name='observation-options-list'),
    path('teacher_observe/<int:group_id>', TeacherObserveView.as_view(), name='teacher-observe')
]
