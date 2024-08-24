from django.urls import path

from transfer.api.turon.user.views import UserJobsTransfer

urlpatterns = [
    path('user/job/', UserJobsTransfer.as_view(), name='user-add-group'),
]
