from django.urls import path

from .Api.createdeleteupdate import StudentCreateView, StudentCharityCreateView, \
    StudentPaymentCreateView, \
    StudentDestroyView, StudentCharityUpdateView, StudentPaymentUpdateView, StudentCharityDestroyView, \
    StudentPaymentDestroyView, StudentUpdateView, StudentHistoryGroupsCreateView, StudentHistoryGroupsDestroyView, \
    StudentHistoryGroupsUpdateView, DeletedStudentDestroy, CreateDiscountForSchool
from .Api.get import SchoolStudents
from .Api.get import StudentCharityAPIView, StudentPaymentAPIView, StudentHistoryGroupsAPIView, \
    StudentCharityListAPIView, StudentPaymentListAPIView, StudentHistoryGroupsListAPIView, StudentRetrieveAPIView, \
    FilteredStudentsListView, StudentDeletedPaymentListAPIView
from .excel import ExcelData, ExcelDataList
from .views import (CreateContractView, UploadPDFContractView, StudentListView, DeletedFromRegistered,
                    DeletedGroupStudents, NewRegisteredStudents, ActiveStudents, PaymentDatas, GetMonth, shahakota,
                    DeleteStudentPayment, DeleteFromDeleted, MissingAttendanceListView, MissingAttendanceView,
                    MissingAttendanceListView2,
                    GetYearView, GetMonthView,
                    StudentCharityModelView, GetStudentBalance
                    )

app_name = 'Students'

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
    path('student_payment_deleted_list/', StudentDeletedPaymentListAPIView.as_view(),
         name='student-deleted-payment-list'),
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
    path('deleted-from-registered/', DeletedFromRegistered.as_view(), name='deleted-from-registered'),
    path('deleted-group-students/', DeletedGroupStudents.as_view(), name='deleted-group-students'),
    path('new-registered-students/', NewRegisteredStudents.as_view(), name='new-registered-students'),
    path('active-students/', ActiveStudents.as_view(), name='active-students'),
    path('school_students/', SchoolStudents.as_view(),
         name='school_students'),
    path('students_for_subject/<int:branch_id>/<int:subject_id>/', SchoolStudents.as_view(),
         name='students_for_subject'),
    path('payment_datas/<int:student_id>/', PaymentDatas.as_view(), name='payment_datas'),
    path('student_payment_month/<int:student_id>/<int:attendance_id>/', GetMonth.as_view(),
         name='student_payment_month'),
    path('student_payment_month_for_month/', shahakota.as_view(),
         name='student_payment_month'),
    path('student_payment_delete_for_month/<int:pk>/', DeleteStudentPayment.as_view(), name='student-payment-delete'),
    path('export-students/', ExcelData.as_view(), name='export_students_excel'),
    path('student-school-list/', ExcelDataList.as_view(), name='export_students_excel'),
    path('delete-student-from-deleted/<int:pk>/', DeleteFromDeleted.as_view()),
    path('missing_month/<int:student_id>/', MissingAttendanceListView.as_view(), name='missing_month'),
    path('missing_month2/<int:student_id>/', MissingAttendanceListView2.as_view(), name='missing_month'),
    path('missing_month_post/<int:student_id>/', MissingAttendanceView.as_view(), name='missing_month'),
    path('discount/', CreateDiscountForSchool.as_view(), name='discount'),
    path('get_year/', GetYearView.as_view(), name='get_year'),
    path('get_month/', GetMonthView.as_view(), name='get_month'),
    path('charity_month/<int:student_id>/', StudentCharityModelView.as_view(), name='charity_month'),
    path('get_balance/<int:user_id>/', GetStudentBalance.as_view())
]
