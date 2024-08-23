from django.urls import path

from .views import TransferWeekDaysCreate

urlpatterns = [
    path('create-week/', TransferWeekDaysCreate.as_view(), name='create-week'),
]
