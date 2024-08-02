from django.urls import path
from .api.get import LeadRetrieveAPIView, LeadListAPIView, LeadCallRetrieveAPIView, LeadCallListAPIView
from .api.createdeleteupdate import LeadCreateView, LeadDestroyView, LeadUpdateView, LeadCallCreateView, \
    LeadCallDestroyView, LeadCallUpdateView

urlpatterns = [
    path('lead_create/', LeadCreateView.as_view(), name='lead-create'),
    path('lead_update/<int:pk>/', LeadUpdateView.as_view(), name='lead-update'),
    path('lead_delete/<int:pk>/', LeadDestroyView.as_view(), name='lead-delete'),
    path('lead/<int:pk>/', LeadRetrieveAPIView.as_view(), name='lead'),
    path('lead_list/', LeadListAPIView.as_view(), name='lead-list'),
    path('lead_call_create/', LeadCallCreateView.as_view(), name='lead-call-create'),
    path('lead_call_update/<int:pk>/', LeadCallUpdateView.as_view(), name='lead-call-update'),
    path('lead_call_delete/<int:pk>/', LeadCallDestroyView.as_view(), name='lead-call-delete'),
    path('lead_call/<int:pk>/', LeadCallRetrieveAPIView.as_view(), name='lead-call'),
    path('lead_call_list/', LeadCallListAPIView.as_view(), name='lead-call-list'),
]
