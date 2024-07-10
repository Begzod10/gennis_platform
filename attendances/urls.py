from django.urls import path

from .Api.ToAttend import ToAttend

urlpatterns = [
    path('to_attend/<int:group_id>/', ToAttend.as_view(), name='to-attend'),
]
