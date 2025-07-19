from django.urls import path
from .api.get import LeadRetrieveAPIView, LeadListAPIView, LeadCallRetrieveAPIView, LeadCallListAPIView, \
    LeadCallTodayListView, OperatorsListView, LeadsByBranchListView
from .api.createdeleteupdate import LeadDestroyView, LeadCallCreateView, \
    lead_call_ring, LeadCreateView,LeadCreateWithTwo

urlpatterns = [

    path('lead_delete/<int:pk>/', LeadDestroyView.as_view(), name='lead-delete'),
    path('lead/<int:pk>/', LeadRetrieveAPIView.as_view(), name='lead'),
    path('lead_list/', LeadListAPIView.as_view(), name='lead-list'),
    path('lead_list_completed/', LeadCallTodayListView.as_view(), name='lead-calls-today'),
    path('lead_call_ring/', lead_call_ring, name='lead_call_ring'),
    path('lead_call_create/', LeadCallCreateView.as_view(), name='lead-call-create'),
    path('lead_create/', LeadCreateView.as_view(), name='lead-create'),
    path('lead_call/<int:pk>/', LeadCallRetrieveAPIView.as_view(), name='lead-call'),
    path('lead_call_list/', LeadCallListAPIView.as_view(), name='lead-call-list'),
    path('operators/', OperatorsListView.as_view(), name='lead-call-list'),
    path('leads_by_branch/', LeadsByBranchListView.as_view(), name='lead-call-list'),
    path('lead_create_with_two/', LeadCreateWithTwo.as_view(), name='lead-create-with-two'),
]
