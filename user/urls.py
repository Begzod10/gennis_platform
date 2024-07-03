from django.urls import path
from .views import *

urlpatterns = [
    path('login/', UserRetrieveAPIView.as_view(), name="login"),
    path('users/', UserListCreateView.as_view(), name='user-list-create'),
    path('users/<int:pk>/', UserDetailView.as_view(), name='user-detail'),
]
