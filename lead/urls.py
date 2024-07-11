from django.urls import path

from .views import (CreateLeadList, CreateLeadCallList, LeadCallRetrieveUpdateDestroyAPIView,
                    LeadRetrieveUpdateDestroyAPIView)

urlpatterns = [
    path('lead/', CreateLeadList.as_view(), name='lead-list-create'),
    path('lead-call/', CreateLeadCallList.as_view(), name='lead-call-list-create'),
    path('lead/<int:pk>/', LeadRetrieveUpdateDestroyAPIView.as_view(), name='lead-detail'),
    path('lead-call/<int:pk>/', LeadCallRetrieveUpdateDestroyAPIView.as_view(), name='lead-call-detail'),
]
