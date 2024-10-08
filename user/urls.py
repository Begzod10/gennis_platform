from django.urls import path

from user.Api.read import (

    UserListCreateView,
    UserDetailView,
    UserSalaryListListView,
    UserSalaryListDetailView,
    UserMe,
    EmployeersListView,
    EmployerRetrieveView,
    UserSalaryMonthView,
    UsersWithJob,
    DeletedUserSalaryListListView
)
from user.Api.write import (
    UserCreateView,
    UserUpdateView,
    UserDestroyView,
    UserSalaryListCreateView,
    UserSalaryListUpdateView,
    UserSalaryListDestroyView,
    UsernameCheck
)
app_name = 'user'
urlpatterns = [
    path('users/create/', UserCreateView.as_view(), name='user-create'),
    path('users/update/<int:pk>/', UserUpdateView.as_view(), name='user-update'),
    path('users/delete/<int:pk>/', UserDestroyView.as_view(), name='user-delete'),
    path('users/', UserListCreateView.as_view(), name='user-list-create'),
    path('users/<int:pk>/', UserDetailView.as_view(), name='user-detail'),
    path('salaries/create/', UserSalaryListCreateView.as_view(), name='salary-create'),
    path('salaries/update/<int:pk>/', UserSalaryListUpdateView.as_view(), name='salary-update'),
    path('salaries/delete/<int:pk>/', UserSalaryListDestroyView.as_view(), name='salary-delete'),
    path('salaries/', UserSalaryListListView.as_view(), name='salary-list'),
    path('salaries-deleted/', DeletedUserSalaryListListView.as_view(), name='salary-list'),
    path('salaries/<int:pk>/', UserSalaryListDetailView.as_view(), name='salary-detail'),
    path('users/me/', UserMe.as_view(), name='user-me'),
    path('employeers/', EmployeersListView.as_view(), name='employer-list'),
    path('employers/<int:pk>/', EmployerRetrieveView.as_view(), name='employer-retrieve'),
    path('username-check/', UsernameCheck.as_view(), name='username-check'),
    path('users-job/', UsersWithJob.as_view(), name='user-jobs'),
    path('user-salary/<int:pk>/', UserSalaryMonthView.as_view(), name='usersalary-check'),
]
