from django.urls import path, include

urlpatterns = [
    path('students/', include('transfer.api.students.urls')),
    path('groups/', include('transfer.api.group.urls')),
    path('teachers/', include('transfer.api.teacher.urls')),
    path('attendance/', include('transfer.api.attendance.urls')),
]
