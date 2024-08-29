from django.urls import path

from transfer.api.gennis.user.views import StaffTransferView, \
    UserJobsTransfer

urlpatterns = [
    path('staff/create/', StaffTransferView.as_view(), name='staff-create'),
    path('user/job/', UserJobsTransfer.as_view(), name='user-add-group'),

]