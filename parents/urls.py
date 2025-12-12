from django.urls import path, include

from parents.views.add_student import AddStudentsView, RemoveStudentsView, AvailableStudentsView, StudentPaymentListView
from parents.views.crud import ParentCreateView, ParentDetailView, ParentListView

urlpatterns = [
    path("create/", ParentCreateView.as_view()),
    path("detail/<int:id>/", ParentDetailView.as_view()),
    path("list/<int:branch_id>/", ParentListView.as_view()),
    path("<int:id>/add_students/", AddStudentsView.as_view()),
    path("<int:id>/remove_student/", RemoveStudentsView.as_view()),
    path("<int:id>/available_students/", AvailableStudentsView.as_view()),
    path("student_payments/", StudentPaymentListView.as_view()),
]
