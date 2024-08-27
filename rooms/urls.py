from django.urls import path

from rooms.Api.createupdatedelete import RoomCreateView, RoomDeleteView, RoomUpdateView, RoomImagesCreateView, \
    RoomImagesUpdateView, RoomImagesDestroyView, RoomSubjectCreateView, RoomSubjectUpdateView, RoomSubjectDestroyView
from rooms.Api.get import RoomListView, RoomRetrieveView, RoomImagesListView, RoomImagesRetrieveView, RoomSubjectListView, \
    RoomSubjectRetrieveView
app_name = 'rooms'
urlpatterns = [
    path('rooms/', RoomListView.as_view(), name='room-list'),
    path('rooms_create/', RoomCreateView.as_view(), name='room-create'),
    path('rooms_delete/<int:pk>/', RoomDeleteView.as_view(), name='room-delete'),
    path('rooms_update/<int:pk>/', RoomUpdateView.as_view(), name='room-update'),
    path('rooms/<int:pk>/', RoomRetrieveView.as_view(), name='room-retrieve'),
    path('rooms_image/', RoomImagesListView.as_view(), name='room-image'),
    path('rooms_image_create/', RoomImagesCreateView.as_view(), name='room-image-create'),
    path('rooms_image_delete/<int:pk>/', RoomImagesDestroyView.as_view(), name='room-image-delete'),
    path('rooms_image_update/<int:pk>/', RoomImagesUpdateView.as_view(), name='room-image-update'),
    path('rooms_image/<int:pk>/', RoomImagesRetrieveView.as_view(), name='room-image-retrieve'),
    path('rooms_subject/', RoomSubjectListView.as_view(), name='room-subject'),
    path('rooms_subject_create/', RoomSubjectCreateView.as_view(), name='room-subject-create'),
    path('rooms_subject_delete/<int:pk>/', RoomSubjectDestroyView.as_view(), name='room-subject-delete'),
    path('rooms_subject_update/<int:pk>/', RoomSubjectUpdateView.as_view(), name='room-subject-update'),
    path('rooms_subject/<int:pk>/', RoomSubjectRetrieveView.as_view(), name='room-subject-retrieve'),
]
