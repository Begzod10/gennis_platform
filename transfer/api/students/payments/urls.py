from django.urls import path, include

from .views import StudentPaymentCreateView

urlpatterns = [
    path('students_payment_create/', StudentPaymentCreateView.as_view(), name='students-create'),

]
