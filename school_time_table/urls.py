from django.urls import path

from .Api.Hours.CreateHour import HourListCreateView
from .Api.TimeTable.CreateClassTimeTable import CreateClassTimeTable
from .Api.TimeTable.UpdateClassTimeTable import UpdateClassTimeTable

urlpatterns = [
    path('hours-list-create/', HourListCreateView.as_view(), name='hours-list-create'),
    path('timetable-list-create/', CreateClassTimeTable.as_view(), name='timetable-list-create'),
    path('timetable-list-update/<int:pk>', UpdateClassTimeTable.as_view(), name='timetable-list-update'),
]
