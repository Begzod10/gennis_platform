from django.urls import path

from Calendar.Api.get import CalendarView, TypeDayListView, TypeDayDetailView
from Calendar.Api.post import ChangeTypeView, TypeDayCreateView, TypeDayUpdateView, TypeDayDestroyView

urlpatterns = [
    path('type_day/', TypeDayListView.as_view(), name='type_day-list'),
    path('type_day_create/', TypeDayCreateView.as_view(), name='type_day-create'),
    path('type_day_delete/<int:pk>/', TypeDayDestroyView.as_view(), name='type_day-delete'),
    path('type_day_update/<int:pk>/', TypeDayUpdateView.as_view(), name='type_day-update'),
    path('type_days/<int:pk>/', TypeDayDetailView.as_view(), name='type_day-retrieve'),
    path('get-calendar/<int:current_year>/<int:next_year>/', CalendarView.as_view(), name='get-calendar'),
    path('change-type/', ChangeTypeView.as_view(), name='change-type'),
]
