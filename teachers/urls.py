from django.urls import path

from .views import (
    TeacherListCreateView, TeacherRetrieveUpdateDestroyView, TeacherSalaryListCreateAPIView,
    TeacherSalaryListDetailAPIView, TeacherSalaryCreateAPIView, TeacherGroupStatisticsListView
)
from .api.get import TeacherAttendanceListView, TeacherAttendanceRetrieveView
from .api.createdeleteupdate import TeacherAttendanceCreateView, TeacherAttendanceDestroyView

urlpatterns = [
    path('teacher_attendance_create/', TeacherAttendanceCreateView.as_view(), name='teacher-attendance-create'),
    path('teacher_attendance_delete/<int:pk>/', TeacherAttendanceDestroyView.as_view(),
         name='teacher-attendance-delete'),
    path('teacher_attendance/<int:pk>/', TeacherAttendanceRetrieveView.as_view(), name='teacher-attendance'),
    path('teacher_attendance_list/', TeacherAttendanceListView.as_view(), name='teacher-attendance-list'),
    path('teachers/', TeacherListCreateView.as_view(), name='teacher-list-create'),
    path('teacher-statistics-view/', TeacherGroupStatisticsListView.as_view(),
         name='teacher-statistics-view-list-create'),
    path('teachers/<int:pk>/', TeacherRetrieveUpdateDestroyView.as_view(), name='teacher-detail'),
    path('teacher-salary-list/', TeacherSalaryListCreateAPIView.as_view(), name='teacher-salary-list'),
    path('teacher-salary/', TeacherSalaryCreateAPIView.as_view(), name='teacher-salary'),

    path('teacher-salary-list/<int:pk>/', TeacherSalaryListDetailAPIView.as_view(), name='teacher-salary-detail-list'),

]
