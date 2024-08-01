from django.urls import path

from .Api.Hours.CreateHour import HourListCreateView
from .Api.Hours.UpdateHour import HourUpdateDeleteView
from .Api.TimeTable.CreateClassTimeTable import CreateClassTimeTable, Classes, ClassTimeTableLessonsView
from .Api.TimeTable.UpdateClassTimeTable import UpdateClassTimeTable
from .Api.TimeTable.DeleteItemClassTimeTable import DeleteItemClassTimeTable

urlpatterns = [
    path('hours-list-create/', HourListCreateView.as_view(), name='hours-list-create'),
    path('hours-list-update/<int:pk>', HourUpdateDeleteView.as_view(), name='hours-list-update'),
    path('timetable-list-create/', CreateClassTimeTable.as_view(), name='timetable-list-create'),
    path('timetable-list-update/<int:pk>', UpdateClassTimeTable.as_view(), name='timetable-list-update'),
    path('timetable-list-delete_item/<int:pk>', DeleteItemClassTimeTable.as_view(), name='timetable-list-delete_item'),
    path('timetable-classes/<int:pk>', Classes.as_view(), name='timetable-list-delete_item'),
    path('class-timetable/<int:pk>', ClassTimeTableLessonsView.as_view(), name='timetable-list-delete_item'),
]
