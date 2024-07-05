from django.urls import path

from .views import DeleteGroups, CreatGroups, GroupProfile, AddToGroupApi, MoveToGroupApi

urlpatterns = [
    path('groups/create/', CreatGroups.as_view(), name='create'),
    path('groups/profile/<int:pk>/', GroupProfile.as_view(), name='profile'),
    path('groups/delete/<int:pk>/', DeleteGroups.as_view(), name='delete'),
    path('groups/add-to-group/<int:pk>/', AddToGroupApi.as_view(), name='add-to-group-api'),
    path('groups/move-to-group/<int:pk>/', MoveToGroupApi.as_view(), name='movie-to-group-api'),
]
