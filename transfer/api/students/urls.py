from django.urls import path
from .views import StudentCreateView, StudentHistoryGroupView, StudentCharityView

urlpatterns = [
    path('students_create/', StudentCreateView.as_view(), name='students-create'),
    path('students-history-group/', StudentHistoryGroupView.as_view(), name='students-history-group'),
    path('students-charity/', StudentCharityView.as_view(), name='students-charity'),
]
