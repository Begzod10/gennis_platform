from django.urls import path

from .views import (Encashments, GetSchoolStudents,GetTeacherSalary,GetEMployerSalary,EncashmentsSchool,OneDayReportView)

urlpatterns = [
    path('encashment/', Encashments.as_view(), name='encashment'),
    path('encashment/<int:pk>/', Encashments.as_view(), name='encashment'),
    path('student_payments/', GetSchoolStudents.as_view(), name='student_payments'),
    path('teacher_salary/', GetTeacherSalary.as_view(), name='student_payments'),
    path('employer_salary/', GetEMployerSalary.as_view(), name='student_payments'),
    path('encashment_school/', EncashmentsSchool.as_view(), name='encashment'),
    path('one_day_report/', OneDayReportView.as_view(), name='one_day_report'),

]
