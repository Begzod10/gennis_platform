from django.urls import path
from .views import (
    RoomListCreateView,
    RoomRetrieveUpdateDestroyView,
    RoomImagesListCreateView,
    RoomImagesRetrieveUpdateDestroyView,
    RoomSubjectListCreateView,
    RoomSubjectRetrieveUpdateDestroyView,
)

urlpatterns = [
    path('rooms/', RoomListCreateView.as_view(), name='room-list-create'),
    path('rooms/<int:pk>/', RoomRetrieveUpdateDestroyView.as_view(), name='room-retrieve-update-destroy'),
    path('room-images/', RoomImagesListCreateView.as_view(), name='room-images-list-create'),
    path('room-images/<int:pk>/', RoomImagesRetrieveUpdateDestroyView.as_view(), name='room-images-retrieve-update-destroy'),
    path('room-subjects/', RoomSubjectListCreateView.as_view(), name='room-subjects-list-create'),
    path('room-subjects/<int:pk>/', RoomSubjectRetrieveUpdateDestroyView.as_view(), name='room-subjects-retrieve-update-destroy'),
]
