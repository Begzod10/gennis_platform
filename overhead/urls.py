from django.urls import path
from .views import OverheadListCreateView, OverheadRetrieveUpdateDestroyView

urlpatterns = [
    path('overheads/', OverheadListCreateView.as_view(), name='overhead-list-create'),
    path('overheads/<int:pk>/', OverheadRetrieveUpdateDestroyView.as_view(), name='overhead-detail'),
]
