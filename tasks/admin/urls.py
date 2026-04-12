from django.urls import path


from tasks.admin.tasks import (
    DebtorsAPIView,
)
from tasks.admin.vats.api.views import CallAsyncView


urlpatterns = [
    path("debtors/", DebtorsAPIView.as_view()),
    path("calls/", CallAsyncView.as_view()),
]
