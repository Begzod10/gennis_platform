from django.urls import path, include
from .views import *

urlpatterns = [
    path('branch/', CreateBranchList.as_view(), name='branch-list-create'),
    path('branch/<int:pk>/', BranchRetrieveUpdateDestroyAPIView.as_view(), name='branch-detail'),
]
