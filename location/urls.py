from django.urls import path

from .api.get import LocationRetrieveAPIView, LocationListAPIView, LocationsForSystem,LocationsForSystemBranh
from .api.createdeleteupdate import LocationCreateView, LocationDestroyView, LocationUpdateView

urlpatterns = [
    path('location_create/', LocationCreateView.as_view(), name='location-create'),
    path('location_update/<int:pk>/', LocationUpdateView.as_view(), name='location-update'),
    path('location_delete/<int:pk>/', LocationDestroyView.as_view(), name='location-delete'),
    path('location/<int:pk>/', LocationRetrieveAPIView.as_view(), name='location'),
    path('location_list/', LocationListAPIView.as_view(), name='location-list'),
    path('location_for_system/', LocationsForSystem.as_view(), name='location_for_system'),
    path('location_for_system_branch/', LocationsForSystemBranh.as_view(), name='location_for_system'),
]
