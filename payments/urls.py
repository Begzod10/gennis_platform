from django.urls import path


from .views import (
    CreatePaymentTypesList, PaymentTypesRetrieveUpdateAPIView
)

urlpatterns = [
    path('payment_type/', CreatePaymentTypesList.as_view(), name='payment_type-list-create'),
    path('payment_type/<int:pk>/', PaymentTypesRetrieveUpdateAPIView.as_view(), name='payment_type-detail'),
]
