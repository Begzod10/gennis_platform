from django.urls import path

from payments.Api.create_update_delete import (

    PaymentTypesCreate,
    PaymentTypesUpdateAPIView
)
from payments.Api.get import (
    PaymentTypesList,
    PaymentTypesRetrieveAPIView,

)

urlpatterns = [
    path('payment-types/', PaymentTypesList.as_view(), name='paymenttypes-list'),
    path('payment-types/<int:pk>/', PaymentTypesRetrieveAPIView.as_view(), name='paymenttypes-detail'),
    path('payment-types/create/', PaymentTypesCreate.as_view(), name='paymenttypes-create'),
    path('payment-types/update/<int:pk>/', PaymentTypesUpdateAPIView.as_view(), name='paymenttypes-update'),
]
