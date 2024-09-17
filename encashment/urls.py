from django.urls import path

from .views import (Encashments, GetSchoolStudents)

urlpatterns = [
    path('encashment/', Encashments.as_view(), name='encashment'),
    path('encashment/<int:pk>/', Encashments.as_view(), name='encashment'),
    path('student_payments/', GetSchoolStudents.as_view(), name='student_payments'),
]
