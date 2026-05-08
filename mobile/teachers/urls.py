from django.urls import path, include

from .views import TeacherGroupProfileView, TeacherProfileView, SalaryYearsView, TeacherSalaryView, TeacherClassesView, \
    StudentScoreView, TeacherTodayAttendance, TeacherDashboardView, TeacherGetLessonPlanView, \
    TeacherChangeLessonPlanView, TeacherTimeTableView, TeacherStatAPIView
from .lesson_plan_file_views import (
    MobileLessonPlanFileUploadView,
    MobileLessonPlanFileStatusView,
    MobileLessonPlanFileListView,
)
from .terms_views import (
    TeacherEducationYears,
    TeacherListTerm,
    TeacherListTest,
    TeacherCreateTest,
    TeacherUpdateTest,
    TeacherDeleteTest,
    TeacherStudentAssignmentView,
    TeacherAssignmentCreateView,
    TeacherTermsByGroupView,
    TeacherGroupsAndFlowsView,
)

app_name = 'teachers'
urlpatterns = [
    path('group-profile/', TeacherGroupProfileView.as_view(), name='group-profile'),
    path('teacher-profile/', TeacherProfileView.as_view(), name='teacher-profile'),
    path('salary-years/', SalaryYearsView.as_view(), name='salary-years'),
    path('teacher-salary/', TeacherSalaryView.as_view(), name='teacher-salary'),
    path('teacher-classes/', TeacherClassesView.as_view(), name='teacher-classes'),
    path('student-score/', StudentScoreView.as_view(), name='student-score'),
    path("teacher/today-attendance/", TeacherTodayAttendance.as_view(), name="teacher-today-attendance"),
    path("teacher/dashboard/", TeacherDashboardView.as_view(), name="teacher-dashboard"),
    path("teacher/timetable/", TeacherTimeTableView.as_view(), name="teacher-timetable"),
    path("teacher/stat/", TeacherStatAPIView.as_view(), name="teacher-stat"),

    path("teacher/lesson-plan/", TeacherGetLessonPlanView.as_view()),
    path('teacher/change_lesson_plan/<int:pk>/', TeacherChangeLessonPlanView.as_view(), name='change_lesson_plan'),
    # path('payments/', TeacherPaymentsListView.as_view(), name='teacher-payments'),
    # path('debted-students/', TeachersDebtedStudentsListView.as_view(), name='debted-students'),
    # path('attandance-students/', TeachersAttendaceStudentsListView.as_view(), name='debted-students'),
    # path('profile/', TeacherProfileView.as_view(), name='teacher-profile'),
    # path('groups/', GroupListView.as_view(), name='teacher-profile'),
    path('missions/', include('mobile.teachers.missions.urls'), name='missions'),
    path('observation/', include('mobile.teachers.observation.urls'), name='observation'),

    # Lesson plan file upload + AI review
    path('lesson-plan/file/upload/', MobileLessonPlanFileUploadView.as_view(), name='mobile-lp-upload'),
    path('lesson-plan/file/<int:pk>/', MobileLessonPlanFileStatusView.as_view(), name='mobile-lp-status'),
    path('lesson-plan/file/', MobileLessonPlanFileListView.as_view(), name='mobile-lp-list'),

    # Terms (Baholash/Choraklar)
    path('terms/education-years/', TeacherEducationYears.as_view(), name='terms-education-years'),
    path('terms/list-term/<str:academic_year>/', TeacherListTerm.as_view(), name='terms-list-term'),
    path('terms/list-test/<int:term>/', TeacherListTest.as_view(), name='terms-list-test'),
    path('terms/create-test/', TeacherCreateTest.as_view(), name='terms-create-test'),
    path('terms/update-test/<int:pk>/', TeacherUpdateTest.as_view(), name='terms-update-test'),
    path('terms/delete-test/<int:pk>/', TeacherDeleteTest.as_view(), name='terms-delete-test'),
    path('terms/student-assignment/<int:group_id>/<int:test_id>/', TeacherStudentAssignmentView.as_view(),
         name='terms-student-assignment'),
    path('terms/assignment-create/', TeacherAssignmentCreateView.as_view(), name='terms-assignment-create'),
    path('terms/terms-by-group/<int:group_id>/<int:term_id>/', TeacherTermsByGroupView.as_view(),
         name='terms-by-group'),
    path('terms/terms-by-group/<int:group_id>/<int:term_id>/<int:subject_id>/', TeacherTermsByGroupView.as_view(),
         name='terms-by-group-subject'),
    path('terms/my-classes/', TeacherGroupsAndFlowsView.as_view(), name='terms-my-classes'),
]
