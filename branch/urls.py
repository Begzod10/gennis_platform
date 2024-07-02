from django.urls import path
from . import views

urlpatterns = [
    path('create-branch/', views.create_branch, name="create_branch"),
]
