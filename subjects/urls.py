from django.urls import path
from subjects.views import SyncSubjectsAndLevelsView

urlpatterns = [
    path('sync/subjects/', SyncSubjectsAndLevelsView.as_view(), name='sync_subjects'),
]
