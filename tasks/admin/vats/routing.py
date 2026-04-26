from django.urls import re_path
from tasks.admin.vats.consumers import CallStatusConsumer,TestConsumer

websocket_urlpatterns = [
    re_path(r'ws/call/(?P<callid>\w+)/$', CallStatusConsumer.as_asgi()),
    re_path(r'ws/test/$', TestConsumer.as_asgi()),

]
