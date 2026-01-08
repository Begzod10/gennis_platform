from django.urls import path

from .views import TeacherGroupProfileView, TeacherProfileView, SalaryYearsView, TeacherSalaryView, TeacherClassesView, \
    StudentScoreView, TeacherTodayAttendance

app_name = 'teachers'
urlpatterns = [
    path('group-profile/', TeacherGroupProfileView.as_view(), name='group-profile'),
    path('teacher-profile/', TeacherProfileView.as_view(), name='teacher-profile'),
    path('salary-years/', SalaryYearsView.as_view(), name='salary-years'),
    path('teacher-salary/', TeacherSalaryView.as_view(), name='teacher-salary'),
    path('teacher-classes/', TeacherClassesView.as_view(), name='teacher-classes'),
    path('student-score/', StudentScoreView.as_view(), name='student-score'),
    path( "teacher/today-attendance/",TeacherTodayAttendance.as_view(),name="teacher-today-attendance"),
]
