from django.urls import path

from .views import (
    StudentCharityListCreate, StudentCharityRetrieveUpdateDestroy,
    StudentListCreateView, StudentRetrieveUpdateDestroyView,
    StudentHistoryGroupsRetrieveUpdateDestroyView,
    StudentPaymentRetrieveUpdateDestroyView,
    StudentPaymentListCreateView

)

urlpatterns = [
    path('students/', StudentListCreateView.as_view(), name='student-list-create'),
    path('students/<int:pk>/', StudentRetrieveUpdateDestroyView.as_view(), name='student-detail'),
    # path('student_history_groups/', StudentHistoryGroupsListCreateView.as_view(),
    #      name='student-history-groups-list-create'),
    path('student_history_groups/<int:pk>/', StudentHistoryGroupsRetrieveUpdateDestroyView.as_view(),
         name='student-history-groups-detail'),

    path('student-charities/', StudentCharityListCreate.as_view(), name='student-charity-list-create'),
    path('student-charities/<int:pk>/', StudentCharityRetrieveUpdateDestroy.as_view(),
         name='student-charity-retrieve-update-destroy'),
    path('student_payment/', StudentPaymentListCreateView.as_view(),
         name='student-payment-list-create'),
    path('student_payment/<int:pk>/', StudentPaymentRetrieveUpdateDestroyView.as_view(),
         name='student-payment-detail'),
]
