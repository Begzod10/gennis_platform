from django.urls import path

from teachers.Api.read import (
    TeacherGroupStatisticsListView,
    TeacherListView,
    TeacherRetrieveView,
    TeacherSalaryListAPIView,
    TeacherSalaryDetailAPIView,
    TeacherSalaryDetailAPIView2,
    TeacherSalaryListView, TeacherSalaryListDetailView, GetTeacherBalance, TeacherSalaryListDetailView2,
    TeacherFaceIdView
)
from teachers.Api.write import (
    TeacherCreateView, TeacherUpdateView, TeacherDestroyView,
    TeacherSalaryCreateAPIView, TeacherSalaryDeleteAPIView, TeacherSalaryUpdateAPIView, TeacherSalaryUpdateAPIViewPatch,
    UploadFile, SalaryTypeUpdate
)
from .Api.createdeleteupdate import TeacherAttendanceCreateView, TeacherAttendanceDestroyView
from .Api.get import TeacherAttendanceListView, TeacherAttendanceRetrieveView, TeachersForBranches, TeachersForSubject, \
    SalaryType, TeachersForSubjectForTimeTable
from .views import GetGroupStudents

app_name = 'Teachers'

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
    path('teacher-salary-list2/<int:pk>/', TeacherSalaryDetailAPIView2.as_view(), name='teacher-salary-detail-Api'),
    path('teacher-salary-list-month/<int:pk>/', TeacherSalaryListDetailView.as_view(),
         name='teacher-salary-detail-Api'),
    path('teacher-salary-list-month2/<int:pk>/', TeacherSalaryListDetailView2.as_view(),
         name='teacher-salary-detail-Api'),
    path('teacher-salaries/', TeacherSalaryListView.as_view(), name='teacher-salary-list'),
    path('teachers/create/', TeacherCreateView.as_view(), name='teacher-create'),
    path('teachers/update/<int:pk>/', TeacherUpdateView.as_view(), name='teacher-update'),
    path('teachers/delete/<int:pk>/', TeacherDestroyView.as_view(), name='teacher-delete'),
    path('teachers/salary/create/', TeacherSalaryCreateAPIView.as_view(), name='teacher-salary-create'),
    path('teachers/salary/delete/<int:pk>/', TeacherSalaryDeleteAPIView.as_view(), name='teacher-salary-delete'),
    path('teachers/salary/update/<int:pk>/', TeacherSalaryUpdateAPIView.as_view(), name='teacher-salary-update'),
    path('teachers/salary/update_patch/<int:pk>/', TeacherSalaryUpdateAPIViewPatch.as_view(),
         name='teacher-salary-update'),
    path('teachers-for-branches/<int:pk>/', TeachersForBranches.as_view(), name='teachers-for-branches'),
    path('upload-file/', UploadFile.as_view(), name='upload-file'),
    path('teachers-for-subject/', TeachersForSubject.as_view(),
         name='teachers-for-subject'),
    path('teachers-for-subject-time/', TeachersForSubjectForTimeTable.as_view(),
         name='teachers-for-subject'),
    path('salary-types/', SalaryType.as_view(),
         name='salary-types'),
    path('salary-types/<int:pk>/', SalaryTypeUpdate.as_view(),
         name='salary-types'),
    path('group-student/<int:pk>/', GetGroupStudents.as_view(),
         name='group-student'),
    path('get_balance/<int:user_id>/', GetTeacherBalance.as_view()),
    path('teacher_face_id/', TeacherFaceIdView.as_view())
]
