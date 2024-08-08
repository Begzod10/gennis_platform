from django.urls import path

from .views import TransferCreatAttendancePerMonth

urlpatterns = [
    path('create/', TransferCreatAttendancePerMonth.as_view(), name='create'),
]
