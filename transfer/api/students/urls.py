from django.urls import path,include
from .views import StudentCreateView

urlpatterns = [
    path('students_create/', StudentCreateView.as_view(), name='students-create'),
    path('', include('transfer.api.students.payments.urls')),

]
