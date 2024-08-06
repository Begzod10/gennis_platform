from django.urls import path

from .views import TransferCreatGroups

urlpatterns = [
    path('create/', TransferCreatGroups.as_view(), name='create'),
]
