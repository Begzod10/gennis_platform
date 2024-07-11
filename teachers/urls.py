from django.urls import path

from .views import (

    TeacherListCreateView, TeacherRetrieveUpdateDestroyView, TeacherSalaryListCreateAPIView,
    TeacherSalaryListDetailAPIView, TeacherSalaryCreateAPIView, TeacherGroupStatisticsListView
)

urlpatterns = [
    path('teachers/', TeacherListCreateView.as_view(), name='teacher-list-create'),
    path('teacher-statistics-view/', TeacherGroupStatisticsListView.as_view(),
         name='teacher-statistics-view-list-create'),
    path('teachers/<int:pk>/', TeacherRetrieveUpdateDestroyView.as_view(), name='teacher-detail'),
    path('teacher-salary-list/', TeacherSalaryListCreateAPIView.as_view(), name='teacher-salary-list'),
    path('teacher-salary/', TeacherSalaryCreateAPIView.as_view(), name='teacher-salary'),

    path('teacher-salary-list/<int:pk>/', TeacherSalaryListDetailAPIView.as_view(), name='teacher-salary-detail-list'),

]
