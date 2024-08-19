from django.urls import path

from transfer.api.user.views import StaffTransferView, StaffSalaryTransferView, StaffSalaryListTransferView, \
    UserJobsTransfer

urlpatterns = [
    path('staff/create/', StaffTransferView.as_view(), name='staff-create'),
    path('staff/salary/', StaffSalaryTransferView.as_view(), name='staff-salary'),
    path('staff/salary_list/', StaffSalaryListTransferView.as_view(), name='staff-salary'),
    path('user/job/', UserJobsTransfer.as_view(), name='user-add-group'),

]