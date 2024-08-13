from django.urls import path, include

urlpatterns = [
    path('students/', include('transfer.api.students.urls')),
    path('teachers/', include('transfer.api.teacher.urls')),
    path('groups/', include('transfer.api.group.urls')),
    path('attendance/', include('transfer.api.attendance.urls')),
    path('users/', include('transfer.api.user.urls')),

]
