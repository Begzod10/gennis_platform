from django.urls import path

from .Api.Hours.CreateHour import HourListCreateView, HoursView

from .Api.Hours.UpdateHour import HourUpdateDeleteView
from .Api.TimeTable.CreateClassTimeTable import CreateClassTimeTable, ClassesFlows, ClassTimeTableLessonsView, \
    CheckClassTimeTable, ClassTimeTableForClassView
from .Api.TimeTable.UpdateClassTimeTable import UpdateClassTimeTable, UpdateClassTimeTableHours, UpdateFlowTimeTable
from .Api.TimeTable.DeleteItemClassTimeTable import DeleteItemClassTimeTable
from .Api.TimeTable.checks.checkNextLesson import CheckNextLesson
from .views import TimeTableAPIView, TimeTableDataView

urlpatterns = [
    path('hours-list-create/', HourListCreateView.as_view(), name='hours-list-create'),
    path('hours-list-for-type/', HoursView.as_view(), name='hours-list-for-type'),
    path('hours-list-update/<int:pk>', HourUpdateDeleteView.as_view(), name='hours-list-update'),
    path('timetable-list-create/', CreateClassTimeTable.as_view(), name='timetable-list-create'),
    path('timetable-list-update/<int:pk>', UpdateClassTimeTable.as_view(), name='timetable-list-update'),
    path('timetable-list-delete_item/<int:pk>', DeleteItemClassTimeTable.as_view(), name='timetable-list-delete_item'),
    path('timetable-list-delete/<int:pk>', DeleteItemClassTimeTable.as_view(), name='timetable-list-delete_item'),
    # path('timetable-classes/<int:pk>', Classes.as_view(), name='timetable-list-delete_item'),
    path('timetable-class-flow/', ClassesFlows.as_view(), name='timetable-classes'),
    path('timetable-update-hours-rooms/', UpdateClassTimeTableHours.as_view(), name='timetable-update-hours-rooms'),
    path('timetable-lessons/', ClassTimeTableLessonsView.as_view(), name='timetable-lessons'),
    path('timetable-lessons-class/', ClassTimeTableForClassView.as_view(), name='timetable-lessons-class'),
    path('can-set/', CheckClassTimeTable.as_view(), name='timetable-lessons'),
    path('can-set-flow/', UpdateFlowTimeTable.as_view(), name='timetable-lessons'),
    path('check-next-lesson/', CheckNextLesson.as_view(),
         name='check-next-lesson'),
    path('time_table_mobile/<int:pk>/', TimeTableAPIView.as_view(), name='time_table_mobile'),
    path('time_table_data_view/', TimeTableDataView.as_view(), name='time_table_data_view'),
]
