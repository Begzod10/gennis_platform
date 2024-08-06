from django.urls import path
from .views import StudentCreateView

urlpatterns = [
    path('user/', StudentCreateView.as_view(), name='students-create'),
]
