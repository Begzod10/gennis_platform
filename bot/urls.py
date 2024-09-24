from django.urls import path
from .views import get_user_with_telegram_username, get_user_with_passport_number, get_user_with_username_and_password, \
    get_table_with_student_username, get_table_week_with_student_username, get_attendances_with_student_username, \
    check_student, logout_student,parent_choose,parent_active,logout_parent

urlpatterns = [
    path('login_parent', get_user_with_telegram_username.as_view(), name='login_parent'),
    path('login_student', get_user_with_username_and_password.as_view(), name='login_student'),
    path('logout_student', logout_student.as_view(), name='login_student'),
    path('logout_parent', logout_parent.as_view(), name='login_student'),
    path('parent_choose', parent_choose.as_view(), name='parent_choose'),
    path('parent_active', parent_active.as_view(), name='parent_choose'),
    path('check_student', check_student.as_view(), name='check_student'),
    path('get_attendances_with_student_username', get_attendances_with_student_username.as_view(),
         name='get_attendances_with_student_username'),
    path('get_table_with_student_username', get_table_with_student_username.as_view(),
         name='get_table_with_student_username'),
    path('get_table_week_with_student_username', get_table_week_with_student_username.as_view(),
         name='get_table_week_with_student_username'),
    path('get_user_with_passport_number', get_user_with_passport_number.as_view(),
         name='get_user_with_passport_number'),
]
