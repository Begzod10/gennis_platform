from django.urls import path
from .views import StudentCreateView

urlpatterns = [
    path('students_create/', StudentCreateView.as_view(), name='students-create'),
]
