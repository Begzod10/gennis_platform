from django.urls import path
from .views import CreateTest, UpdateTest, ListTest,ListTerm

urlpatterns = [
    path('create-test/', CreateTest.as_view(), name='create-test'),
    path('update-test/<int:pk>/', UpdateTest.as_view(), name='update-test'),
    path('list-test/<int:term>/<int:branch>/', ListTest.as_view(), name='list-test'),
    path('list-term/', ListTerm.as_view(), name='list-term'),
]