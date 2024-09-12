from django.urls import path, include
from .views import get_user_with_telegram_username, get_user_with_passport_number, get_user_with_username_and_password, \
    get_table_with_student_username

urlpatterns = [
    path('login_parent', get_user_with_telegram_username.as_view(), name='login'),
    path('login_student', get_user_with_username_and_password.as_view(), name='login'),
    path('get_table_with_student_username', get_table_with_student_username.as_view(), name='login'),
    path('get_user_with_passport_number', get_user_with_passport_number.as_view(), name='login'),
]
