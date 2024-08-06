from django.urls import path, include

urlpatterns = [
    path('students/', include('transfer.api.students.urls')),
    path('teachers/', include('transfer.api.teacher.urls')),
]
