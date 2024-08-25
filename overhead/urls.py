from django.urls import path

from overhead.Api.create_update_delete import (

    OverheadCreateView,
    OverheadUpdateView,
    OverheadDestroyView,
)
from overhead.Api.get import (

    OverheadListView,
    OverheadRetrieveView,
    OverheadTYpeListView,
    MonthDaysView
)

urlpatterns = [
    path('overheads/', OverheadListView.as_view(), name='overhead-list'),
    path('overheads_type/', OverheadTYpeListView.as_view(), name='overhead-list'),
    path('overheads/<int:pk>/', OverheadRetrieveView.as_view(), name='overhead-detail'),
    path('overheads/create/', OverheadCreateView.as_view(), name='overhead-create'),
    path('overheads/<int:pk>/update/', OverheadUpdateView.as_view(), name='overhead-update'),
    path('overheads/delete/<int:pk>/', OverheadDestroyView.as_view(), name='overhead-delete'),
    path('month-days/', MonthDaysView.as_view(), name='month_days'),

]
