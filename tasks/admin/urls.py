from django.urls import path


from tasks.admin.tasks import (
    DebtorsAPIView,
)
from tasks.admin.vats.api.views import CallAPIView


urlpatterns = [
    path("debtors/", DebtorsAPIView.as_view()),
    path("/", CallAPIView.as_view()),
]
