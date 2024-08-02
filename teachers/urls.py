from django.urls import path

from teachers.Api.read import (
    TeacherGroupStatisticsListView,
    TeacherListView,
    TeacherRetrieveView,
    TeacherSalaryListAPIView,
    TeacherSalaryDetailAPIView,
    TeacherSalaryListView,
)
from teachers.Api.write import (
    TeacherCreateView, TeacherUpdateView, TeacherDestroyView,
    TeacherSalaryCreateAPIView, TeacherSalaryDeleteAPIView, TeacherSalaryUpdateAPIView
)
from .Api.get import TeacherAttendanceListView, TeacherAttendanceRetrieveView
from .Api.createdeleteupdate import TeacherAttendanceCreateView, TeacherAttendanceDestroyView

urlpatterns = [
    path('teacher_attendance_create/', TeacherAttendanceCreateView.as_view(), name='teacher-attendance-create'),
    path('teacher_attendance_delete/<int:pk>/', TeacherAttendanceDestroyView.as_view(),
         name='teacher-attendance-delete'),
    path('teacher_attendance/<int:pk>/', TeacherAttendanceRetrieveView.as_view(), name='teacher-attendance'),
    path('teacher_attendance_list/', TeacherAttendanceListView.as_view(), name='teacher-attendance-list'),
    path('teacher-statistics-view/', TeacherGroupStatisticsListView.as_view(),
         name='teacher-statistics-view-list-create'),
    path('teacher-statistics-view/', TeacherGroupStatisticsListView.as_view(), name='teacher-group-statistics-list'),
    path('teachers/', TeacherListView.as_view(), name='teacher-list'),
    path('teachers/<int:pk>/', TeacherRetrieveView.as_view(), name='teacher-retrieve'),
    path('teacher-salary-list/', TeacherSalaryListAPIView.as_view(), name='teacher-salary-list-Api'),
    path('teacher-salary-list/<int:pk>/', TeacherSalaryDetailAPIView.as_view(), name='teacher-salary-detail-Api'),
    path('teacher-salaries/', TeacherSalaryListView.as_view(), name='teacher-salary-list'),
    path('teachers/create/', TeacherCreateView.as_view(), name='teacher-create'),
    path('teachers/update/<int:pk>/', TeacherUpdateView.as_view(), name='teacher-update'),
    path('teachers/delete/<int:pk>/', TeacherDestroyView.as_view(), name='teacher-delete'),
    path('teachers/salary/create/', TeacherSalaryCreateAPIView.as_view(), name='teacher-salary-create'),
    path('teachers/salary/delete/<int:pk>/', TeacherSalaryDeleteAPIView.as_view(), name='teacher-salary-delete'),
    path('teachers/salary/update/<int:pk>/', TeacherSalaryUpdateAPIView.as_view(), name='teacher-salary-update'),

]
