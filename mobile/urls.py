from django.urls import path, include


urlpatterns = [
    path('teachers/', include('mobile.teachers.urls'), name='teacher'),
    path("parents/", include("mobile.parents.urls"), name="parents"),
]
