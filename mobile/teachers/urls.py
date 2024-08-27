from django.urls import path
from .views import TeacherPaymentsListView, TeachersDebtedStudentsListView, TeacherProfileView

urlpatterns = [
    path('payments/', TeacherPaymentsListView.as_view(), name='teacher-payments'),
    path('debted-students/', TeachersDebtedStudentsListView.as_view(), name='debted-students'),
    path('profile/<int:pk>/', TeacherProfileView.as_view(), name='teacher-profile'),
]
