from django.urls import path

from .views import (CreateBranchList, BranchRetrieveUpdateDestroyAPIView)

urlpatterns = [
    path('branch/', CreateBranchList.as_view(), name='branch-list-create'),
    path('branch/<int:pk>/', BranchRetrieveUpdateDestroyAPIView.as_view(), name='branch-detail'),
]
