from django.urls import path

from .Api.FlowTypes import FlowTypesListCreateView, FlowTypesDelete
from .Api.Flow import FlowListCreateView, FlowListView, Flow, FlowProfile

urlpatterns = [
    path('flow-types-list-creat/', FlowTypesListCreateView.as_view(), name='flow-types'),
    path('flow-types-delete/<int:pk>', FlowTypesDelete.as_view(), name='flow-delete'),
    path('flow-list-create/', FlowListCreateView.as_view(), name='flow'),
    path('flow-list/', FlowListView.as_view(), name='flow-list'),
    path('flow-profile/<int:pk>', FlowProfile.as_view(), name='flow-profile'),
]
