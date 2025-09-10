from django.urls import path
from .views import CreateTest, UpdateTest, ListTest,ListTerm,DeleteTest,StudentAssignmentView,AssignmentCreateView,EducationYears

urlpatterns = [
    path('create-test/', CreateTest.as_view(), name='create-test'),
    path('update-test/<int:pk>/', UpdateTest.as_view(), name='update-test'),
    path('list-test/<int:term>/<int:branch>/', ListTest.as_view(), name='list-test'),
    path('list-term/<str:academic_year>/', ListTerm.as_view(), name='list-term'),
    path('delete-test/<int:pk>/', DeleteTest.as_view(), name='delete-test'),
    path('student-assignment/<int:group_id>/<int:test_id>/', StudentAssignmentView.as_view(), name='student-assignment'),
    path('assignment-create/', AssignmentCreateView.as_view(), name='assignment-create'),
    path('education-years/', EducationYears.as_view(), name='education-years'),
]