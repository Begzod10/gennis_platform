from django.urls import path, include

urlpatterns = [
    path('students/', include('transfer.api.students.urls')),
    path('teachers/', include('transfer.api.teacher.urls')),
    path('groups/', include('transfer.api.group.urls')),
    path('attendance/', include('transfer.api.attendance.urls')),
<<<<<<< HEAD

=======
    path('rooms/', include('transfer.api.room.urls')),
    path('time_table/', include('transfer.api.time_table.urls')),
>>>>>>> ec2c4b9d2812b00e218043e55e4207994c67d5e7
]
