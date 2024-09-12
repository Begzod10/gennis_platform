from django.urls import path, include
from .views import get_user_with_telegram_username,get_user_with_passport_number

urlpatterns = [
    path('login', get_user_with_telegram_username.as_view(), name='login'),
    path('get_user_with_passport_number', get_user_with_passport_number.as_view(), name='login'),
]
