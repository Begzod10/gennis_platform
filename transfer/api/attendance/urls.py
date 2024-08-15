from django.urls import path

from .views import TransferCreatAttendancePerMonth, TransferCreatAttendancePerDay

urlpatterns = [
    path('create_month/', TransferCreatAttendancePerMonth.as_view(), name='create-month'),
    path('create_day/', TransferCreatAttendancePerDay.as_view(), name='create-day'),
]
