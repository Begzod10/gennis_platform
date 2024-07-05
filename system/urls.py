from django.urls import path


from .views import (
    CreateSystemList, SystemRetrieveUpdateDestroyAPIView
)


urlpatterns = [
    path('system/', CreateSystemList.as_view(), name='system-list-create'),
    path('system/<int:pk>/', SystemRetrieveUpdateDestroyAPIView.as_view(), name='system-detail'),
]
