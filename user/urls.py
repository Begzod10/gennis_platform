from django.urls import path

from .views import (
    UserListCreateView, UserDetailView, UserSalaryListListCreateView, UserSalaryListDetailView
)


urlpatterns = [
    path('users/', UserListCreateView.as_view(), name='user-list-create'),
    path('users/<int:pk>/', UserDetailView.as_view(), name='user-detail'),
    path('user_salary_list/', UserSalaryListListCreateView.as_view(), name='user-salary-list-detail'),
    path('user_salary_list/<int:pk>/', UserSalaryListDetailView.as_view(), name='user-salary-list-detail'),
]
