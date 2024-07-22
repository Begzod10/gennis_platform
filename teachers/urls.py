from django.urls import path
from .views import (

    TeacherListCreateView, TeacherRetrieveUpdateDestroyView
)

urlpatterns = [
    path('teachers/', TeacherListCreateView.as_view(), name='teacher-list-create'),
    path('teachers/<int:pk>/', TeacherRetrieveUpdateDestroyView.as_view(), name='teacher-detail'),
]
