from django.urls import path

from transfer.api.gennis.user.views import StaffTransferView

urlpatterns = [
    path('staff/create/', StaffTransferView.as_view(), name='staff-create'),
]
