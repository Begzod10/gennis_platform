from django.urls import path

from .views import (Encashments)

urlpatterns = [
    path('encashment/', Encashments.as_view(), name='encashment'),

]
