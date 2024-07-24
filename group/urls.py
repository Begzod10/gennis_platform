from django.urls import path

from .gennis.CreatGroups import CreatGroups, CreateGroupReasonList, GroupReasonRetrieveUpdateDestroyAPIView
from .gennis.GroupProfile import GroupProfile
from .gennis.DeleteGroups import DeleteGroups
from .gennis.AddToGroupApi import AddToGroupApi
from .gennis.TeacherGroupChange import TeacherGroupChange
from .gennis.MoveToGroupApi import MoveToGroupApi

urlpatterns = [
    path('groups/create/', CreatGroups.as_view(), name='create'),
    path('groups/profile/<int:pk>/', GroupProfile.as_view(), name='profile'),
    path('groups/delete/<int:pk>/', DeleteGroups.as_view(), name='delete'),
    path('groups/teacher_change/<int:pk>/', TeacherGroupChange.as_view(), name='change'),
    path('groups/add-to-group/<int:pk>/', AddToGroupApi.as_view(), name='add-to-group-api'),
    path('groups/move-to-group/<int:pk>/', MoveToGroupApi.as_view(), name='movie-to-group-api'),
    path('group_reason/', CreateGroupReasonList.as_view(), name='group-reason-list-create'),
    path('group_reason/<int:pk>/', GroupReasonRetrieveUpdateDestroyAPIView.as_view(), name='group-reason-detail'),
]
