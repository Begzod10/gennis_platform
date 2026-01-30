from django.urls import path, include

from .views import TeacherGroupProfileView, TeacherProfileView, SalaryYearsView, TeacherSalaryView, TeacherClassesView, \
    StudentScoreView, TeacherTodayAttendance, TeacherDashboardView, TeacherGetLessonPlanView, \
    TeacherChangeLessonPlanView

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

    path("teacher/lesson-plan/", TeacherGetLessonPlanView.as_view()),
    path('teacher/change_lesson_plan/<int:pk>/', TeacherChangeLessonPlanView.as_view(), name='change_lesson_plan'),
    # path('payments/', TeacherPaymentsListView.as_view(), name='teacher-payments'),
    # path('debted-students/', TeachersDebtedStudentsListView.as_view(), name='debted-students'),
    # path('attandance-students/', TeachersAttendaceStudentsListView.as_view(), name='debted-students'),
    # path('profile/', TeacherProfileView.as_view(), name='teacher-profile'),
    # path('groups/', GroupListView.as_view(), name='teacher-profile'),
    path('missions/', include('mobile.teachers.missions.urls'), name='missions'),
]
