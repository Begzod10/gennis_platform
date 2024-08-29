from django.urls import path

from .views import (CreateContractView, UploadPDFContractView, StudentListView)
from .Api.get import StudentCharityAPIView, StudentPaymentAPIView, StudentHistoryGroupsAPIView, \
    StudentCharityListAPIView, StudentPaymentListAPIView, StudentHistoryGroupsListAPIView, StudentRetrieveAPIView, \
    FilteredStudentsListView, \
    SchoolStudents
from .Api.createdeleteupdate import StudentCreateView, StudentCharityCreateView, \
    StudentPaymentCreateView, \
    StudentDestroyView, StudentCharityUpdateView, StudentPaymentUpdateView, StudentCharityDestroyView, \
    StudentPaymentDestroyView, StudentUpdateView, StudentHistoryGroupsCreateView, StudentHistoryGroupsDestroyView, \
    StudentHistoryGroupsUpdateView, DeletedStudentDestroy

urlpatterns = [
    path('student_history_groups_create/', StudentHistoryGroupsCreateView.as_view(),
         name='student-history-groups-create'),
    path('student_history_groups_update/<int:pk>/', StudentHistoryGroupsUpdateView.as_view(),
         name='student-history-groups-update'),
    path('student_history_groups_delete/<int:pk>/', StudentHistoryGroupsDestroyView.as_view(),
         name='student-history-groups-delete'),
    path('student_history_groups/<int:pk>/', StudentHistoryGroupsAPIView.as_view(), name='student-history-groups'),
    path('student_history_groups_list/', StudentHistoryGroupsListAPIView.as_view(), name='student-history-groups-list'),
    path('student_charities_create/', StudentCharityCreateView.as_view(), name='student-charities-create'),
    path('student_charities_update/<int:pk>/', StudentCharityUpdateView.as_view(), name='student-charities-update'),
    path('student_charities_delete/<int:pk>/', StudentCharityDestroyView.as_view(), name='student-charities-delete'),
    path('student_charities/<int:pk>/', StudentCharityAPIView.as_view(), name='student-charities'),
    path('student_charities_list/', StudentCharityListAPIView.as_view(), name='student-charities-list'),
    path('student_payment_create/', StudentPaymentCreateView.as_view(), name='student-payment-create'),
    path('student_payment_update/<int:pk>/', StudentPaymentUpdateView.as_view(), name='student-payment-update'),
    path('student_payment_delete/<int:pk>/', StudentPaymentDestroyView.as_view(), name='student-payment-delete'),
    path('student_payment/<int:pk>/', StudentPaymentAPIView.as_view(), name='student-payment'),
    path('student_payment_list/', StudentPaymentListAPIView.as_view(), name='student-payment-list'),
    path('deleted-student/<int:pk>/', DeletedStudentDestroy.as_view(), name='deleted-student-detail'),
    path('students_create/', StudentCreateView.as_view(), name='students-create'),
    path('students_update/<int:pk>/', StudentUpdateView.as_view(), name='students-update'),
    path('students_delete/<int:pk>/', StudentDestroyView.as_view(), name='students-delete'),
    path('students/<int:pk>/', StudentRetrieveAPIView.as_view(), name='students'),
    path('students_list/', StudentListView.as_view(), name='students-list'),
    path('create_contract/<int:user_id>/', CreateContractView.as_view(), name='create_contract'),
    path('upload_pdf_contract/<int:user_id>/', UploadPDFContractView.as_view(), name='upload_pdf_contract'),
    path('api/filter_students_subject/', FilteredStudentsListView.as_view(),
         name='get_filtered_students_list'),
    path('school_students/', SchoolStudents.as_view(),
         name='school_students'),
    path('students_for_subject/<int:branch_id>/<int:subject_id>/', SchoolStudents.as_view(),
         name='students_for_subject'),
]
