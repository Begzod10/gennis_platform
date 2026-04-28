from django.urls import path
from django.urls import re_path

from tasks.admin.tasks import (
    DebtorsAPIView,
    LeadsAPIView
)

from tasks.admin.vats.views import CallAsyncView
from tasks.admin.vats.routing import CallStatusConsumer
from tasks.admin.vats.views import StudentCallHistoryView, CallStatusView, UpdateCallLogView, CallStatisticUpdateView, \
    CallStatisticView, CalledListView

urlpatterns = [
    path("debtors/", DebtorsAPIView.as_view()),
    path("leads/", LeadsAPIView.as_view()),
    path("calls/", CallAsyncView.as_view()),
    path("history/", StudentCallHistoryView.as_view(), name="vats_history"),
    path("status/", CallStatusView.as_view(), name="vats_status"),
    path("update/", UpdateCallLogView.as_view(), name="vats_update"),
    path("statistic/update/", CallStatisticUpdateView.as_view(), name="vats_stat_update"),
    path("statistic/", CallStatisticView.as_view(), name="vats_stat"),
    path("called/", CalledListView.as_view(), name="vats_called"),
    re_path(r'ws/call/(?P<callid>\w+)/$', CallStatusConsumer.as_asgi()),
]
