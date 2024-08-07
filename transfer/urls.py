from django.urls import path, include

urlpatterns = [
    path('students/', include('transfer.api.students.urls')),
<<<<<<< HEAD
    path('groups/', include('transfer.api.group.urls')),
=======
    path('teachers/', include('transfer.api.teacher.urls')),
>>>>>>> da8335d034595c2e9ee6226399a2f5a58a8cb48f
]
