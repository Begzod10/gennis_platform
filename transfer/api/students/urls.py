from django.urls import path, include

from .views import StudentCreateView, DeletedStudentCreateView

urlpatterns = [
    path('students_create/', StudentCreateView.as_view(), name='students-create'),
    path('deleted_students_create/', DeletedStudentCreateView.as_view(), name='deleted-students-create'),
    path('', include('transfer.api.students.payments.urls')),

]
