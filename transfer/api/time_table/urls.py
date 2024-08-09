from django.urls import path

from .views import TransferWeekDaysCreate, TransferGroupTimeTableCreate

urlpatterns = [
    path('create-week/', TransferWeekDaysCreate.as_view(), name='create-week'),
    path('create-group-time_table/', TransferGroupTimeTableCreate.as_view(), name='create-group-time_table'),
]
