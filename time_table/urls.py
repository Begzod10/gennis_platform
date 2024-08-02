from django.urls import path

from .Api.AddGroupTimTable import GroupTimeTableList
from .Api.UpdateGroupTimeTable import GroupTimeTableUpdate
from .Api.time_table_archive import TimeTableArchiveListView, TimeTableArchiveRetrieveAPIView

urlpatterns = [
    path('GrouptimeTableList/<int:group_id>', GroupTimeTableList.as_view(), name='group_time_table_list'),
    path('GrouptimeTableUpdate/<int:pk>/', GroupTimeTableUpdate.as_view(), name='group_time_table_update'),
    path('time_table_archive/<int:pk>/', TimeTableArchiveRetrieveAPIView.as_view(), name='time-table-archive'),
    path('time_table_archive_list/', TimeTableArchiveListView.as_view(), name='time-table-archive-list'),
]
