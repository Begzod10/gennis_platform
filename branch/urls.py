from django.urls import path

from .api.get import BranchRetrieveAPIView, BranchListAPIView
from .api.createdeleteupdate import BranchDestroyView, BranchUpdateView, BranchCreateView

urlpatterns = [
    path('branch_create/', BranchCreateView.as_view(), name='branch-create'),
    path('branch_update/<int:pk>/', BranchUpdateView.as_view(), name='branch-update'),
    path('branch_delete/<int:pk>/', BranchDestroyView.as_view(), name='branch-delete'),
    path('branch/<int:pk>/', BranchRetrieveAPIView.as_view(), name='branch'),
    path('branch_list/', BranchListAPIView.as_view(), name='branch-list'),
]
