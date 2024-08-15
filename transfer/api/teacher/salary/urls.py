from django.urls import path

from .views import TransferTeacherSalaryCreate, TransferTeacherSalaryListCreate, TransferTeacherBlackSalaryCreate

urlpatterns = [
    path('teacher_salary/', TransferTeacherSalaryCreate.as_view(), name='teacher-salary-create'),
    path('teacher_salary_list/', TransferTeacherSalaryListCreate.as_view(), name='teacher-salary-list-create'),
    path('teacher_black_salary/', TransferTeacherBlackSalaryCreate.as_view(), name='teacher-salary-black-create'),

]
