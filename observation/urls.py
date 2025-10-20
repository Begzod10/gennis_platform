from django.urls import path

from .views import (ObservationInfoList, ObservationOptionsList, ObservationInfoRetrieveUpdateAPIView,
                    ObservationOptionsRetrieveUpdateAPIView)
from .api.get import ObservationDayRetrieveAPIView, ObservationDayListView, ObservationStatisticsRetrieveAPIView, \
    ObservationStatisticsListView, TeacherObserveView, ObservedGroupAPIView, ObservedGroupInfoAPIView, \
    ObservedGroupClassroomAPIView, ObservedGroupInfoClassroomAPIView
from .api.createdeleteupdate import ObservationDayCreateView, ObservationDayUpdateView, ObservationDayDestroyView, \
    ObservationStatisticsCreateView, ObservationStatisticsUpdateView, ObservationStatisticsDestroyView

urlpatterns = [
    path('observation_statistics_create/', ObservationStatisticsCreateView.as_view(),
         name='observation-statistics-create'),
    path('observation_statistics_update/<int:pk>/', ObservationStatisticsUpdateView.as_view(),
         name='observation-statistics-update'),
    path('observation_statistics_delete/<int:pk>/', ObservationStatisticsDestroyView.as_view(),
         name='observation-statistics-delete'),
    path('observation_statistics/<int:pk>/', ObservationStatisticsRetrieveAPIView.as_view(),
         name='observation-statistics'),
    path('observation_statistics_list/', ObservationStatisticsListView.as_view(), name='observation-statistics-list'),
    path('observation_day_create/', ObservationDayCreateView.as_view(), name='observation-day-create'),
    path('observation_day_update/<int:pk>/', ObservationDayUpdateView.as_view(), name='observation-day-update'),
    path('observation_day_delete/<int:pk>/', ObservationDayDestroyView.as_view(), name='observation-day-delete'),
    path('observation_day/<int:pk>/', ObservationDayRetrieveAPIView.as_view(), name='observation-day'),
    path('observation_day_list/', ObservationDayListView.as_view(), name='observation-day-list'),
    path('observation_info/', ObservationInfoList.as_view(), name='observation-info-list'),
    path('observation_info/<int:pk>/', ObservationInfoRetrieveUpdateAPIView.as_view(),
         name='observation-info-detail'),
    path('observation_options/', ObservationOptionsList.as_view(), name='observation-options-list'),
    path('observation_options/<int:pk>/', ObservationOptionsRetrieveUpdateAPIView.as_view(),
         name='observation-options-detail'),
    path('teacher_observe/<int:group_id>/', TeacherObserveView.as_view(), name='teacher_observe'),
    path('observed_group/<int:group_id>/', ObservedGroupAPIView.as_view(), name='observed_group_current'),
    path('observed_group/<int:group_id>/<str:date>/', ObservedGroupAPIView.as_view(), name='observed_group_by_date'),
    path('observed_group_info/<int:group_id>/', ObservedGroupInfoAPIView.as_view(), name='observed_group_info'),
    path("observed_group_classroom/<int:group_id>/", ObservedGroupClassroomAPIView.as_view()),
    path("observed_group_classroom/<int:group_id>/<str:date>/", ObservedGroupClassroomAPIView.as_view()),
    path('observed_group_info_classroom/<int:time_table_id>/', ObservedGroupInfoClassroomAPIView.as_view(),
         name='observed_group_info_classroom'),

]
