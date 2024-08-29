from django.urls import path

from .views import TeacherPaymentsListView, TeachersDebtedStudentsListView, TeacherProfileView, \
    TeachersAttendaceStudentsListView, GroupListView

app_name = 'teachers'
urlpatterns = [
    path('payments/', TeacherPaymentsListView.as_view(), name='teacher-payments'),
    path('debted-students/', TeachersDebtedStudentsListView.as_view(), name='debted-students'),
    path('attandance-students/', TeachersAttendaceStudentsListView.as_view(), name='debted-students'),
    path('profile/', TeacherProfileView.as_view(), name='teacher-profile'),
    path('groups/', GroupListView.as_view(), name='teacher-profile'),
]
