from django.urls import path, include

urlpatterns = [
    path('students/', include('transfer.api.students.urls')),
    path('teachers/', include('transfer.api.teacher.urls')),
    path('groups/', include('transfer.api.group.urls')),
    path('attendance/', include('transfer.api.attendance.urls')),
    path('rooms/', include('transfer.api.room.urls')),
    path('time_table/', include('transfer.api.time_table.urls')),
]
