from django.urls import path

from .views import TeacherGroupProfileView, TeacherProfileView

app_name = 'teachers'
urlpatterns = [
    path('group-profile/', TeacherGroupProfileView.as_view(), name='group-profile'),
    path('teacher-profile/', TeacherProfileView.as_view(), name='teacher-profile'),
]
