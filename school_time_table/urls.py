from django.urls import path


urlpatterns = [
    path('students/', StudentListCreateView.as_view(), name='student-list-create'),
]
