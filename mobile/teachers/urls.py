from django.urls import path

from .views import TeacherGroupProfileView

app_name = 'teachers'
urlpatterns = [
    path('group-profile/', TeacherGroupProfileView.as_view(), name='group-profile'),
]
