from django.urls import path

from .views import TransferCreatRooms, TransferCreatRoomImages, TransferCreatRoomSubjects

urlpatterns = [
    path('create-rooms/', TransferCreatRooms.as_view(), name='create-room'),
    path('create-room-images/', TransferCreatRoomImages.as_view(), name='create-room-image'),
    path('create-room-subjects/', TransferCreatRoomSubjects.as_view(), name='create-room-subjects'),
]
