from django.urls import include
from django.urls import path

from .views import StudentCreateView, DeletedStudentCreateView
from .views import StudentHistoryGroupView, StudentCharityView

urlpatterns = [
    path('students_create/', StudentCreateView.as_view(), name='students-create'),
    path('deleted_students_create/', DeletedStudentCreateView.as_view(), name='deleted-students-create'),
    path('students_create/', StudentCreateView.as_view(), name='students-create'),
    path('students-history-group/', StudentHistoryGroupView.as_view(), name='students-history-group'),
    path('students-charity/', StudentCharityView.as_view(), name='students-charity'),
    path('', include('transfer.api.students.payments.urls')),
    ]
