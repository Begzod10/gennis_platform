from django.urls import path, include

urlpatterns = [
    path('students/', include('transfer.api.students.urls')),
]
