from django.urls import path

from .views import InvestorView

urlpatterns = [
    path('investor-report/', InvestorView.as_view(), name='investor-report'),
]