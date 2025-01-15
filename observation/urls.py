from django.urls import path

from .views import (ObservationInfoList, ObservationOptionsList, ObservationInfoRetrieveUpdateAPIView,
                    ObservationOptionsRetrieveUpdateAPIView)
from .api.get import ObservationDayRetrieveAPIView, ObservationDayListView, ObservationStatisticsRetrieveAPIView, \
    ObservationStatisticsListView
from .api.createdeleteupdate import ObservationDayCreateView, ObservationDayUpdateView, ObservationDayDestroyView, \
    ObservationStatisticsCreateView, ObservationStatisticsUpdateView, ObservationStatisticsDestroyView
from observation.new_views import groups_to_observe, teacher_observe, set_observer, observed_group, observed_group_info

urlpatterns = [
    path('groups_to_observe/', groups_to_observe, name='groups_to_observe'),
    path('groups_to_observe/<int:location_id>/', groups_to_observe, name='groups_to_observe_with_location'),

    path('teacher_observe/<int:group_id>/', teacher_observe, name='teacher_observe'),

    path('set_observer/<int:user_id>/', set_observer, name='set_observer'),

    path('observed_group/<int:group_id>/', observed_group, name='observed_group'),
    path('observed_group/<int:group_id>/<str:date>/', observed_group, name='observed_group_with_date'),

    path('observed_group_info/<int:group_id>/', observed_group_info, name='observed_group_info'),

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
]
