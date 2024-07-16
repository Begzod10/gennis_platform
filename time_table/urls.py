from django.urls import path

from .Api.AddGroupTimTable import GroupTimeTableList
from .Api.UpdateGroupTimeTable import GroupTimeTableUpdate

urlpatterns = [
    path('GrouptimeTableList/<int:group_id>', GroupTimeTableList.as_view(), name='group_time_table_list'),
    path('GrouptimeTableUpdate/<int:pk>/', GroupTimeTableUpdate.as_view(), name='group_time_table_update'),
]
