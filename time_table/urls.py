from django.urls import path

from .Api.AddGroupTimTable import CreateGroupTimeTable
from .Api.DeleteTimeTable import TimeTableRetrieveView
from .Api.UpdateGroupTimeTable import GroupTimeTableUpdate
from .Api.time_table_archive import TimeTableArchiveListView, TimeTableArchiveRetrieveAPIView
from .Api.weekDays import WeekDaysView
from .Api.checks.checkGroupNextLesson import CheckGroupNextLesson

urlpatterns = [
    path('GrouptimeTableList/<int:group_id>/', CreateGroupTimeTable.as_view(), name='group_time_table_list'),
    path('GrouptimeTableUpdate/<int:pk>/', GroupTimeTableUpdate.as_view(), name='group_time_table_update'),
    path('time_table_archive/<int:pk>/', TimeTableArchiveRetrieveAPIView.as_view(), name='time-table-archive'),
    path('time_table_delete/<int:pk>/', TimeTableRetrieveView.as_view(), name='time_table_delete'),
    path('time_table_archive_list/', TimeTableArchiveListView.as_view(), name='time-table-archive-list'),
    path('week_days/', WeekDaysView.as_view(), name='week_days'),
    path('check_group_next_lesson/', CheckGroupNextLesson.as_view(), name='check_group_next_lesson'),
]
