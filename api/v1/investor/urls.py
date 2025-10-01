from django.urls import path

from .views import InvestorView, BranchInfoView

urlpatterns = [
    path('investor-report/', InvestorView.as_view(), name='investor-report'),
    path('branch-info/', BranchInfoView.as_view(), name='branch-info'),
]
