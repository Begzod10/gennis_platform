from django.urls import path

from .views import *

urlpatterns = [
    path('location/', CreateLocationList.as_view(), name='location-list-create'),
    path('location/<int:pk>/', LocationRetrieveUpdateDestroyAPIView.as_view(), name='location-detail'),
]
