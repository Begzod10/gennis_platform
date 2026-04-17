from django.urls import re_path
from tasks.admin.vats.consumers import CallStatusConsumer

websocket_urlpatterns = [
    re_path(r'ws/call/(?P<callid>\w+)/$', CallStatusConsumer.as_asgi()),
]
