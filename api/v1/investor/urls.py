from django.urls import path

from .views import InvestorView, BranchInfoView, InvestorReportView, ManagementDividendView, ManagementInvestmentView

urlpatterns = [
    path('investor-report/', InvestorView.as_view(), name='investor-report'),
    path('branch-info/', BranchInfoView.as_view(), name='branch-info'),
    path('report-info/', InvestorReportView.as_view(), name='branch-info'),
    path('dividends/', ManagementDividendView.as_view(), name='management-dividends'),
    path('investments/', ManagementInvestmentView.as_view(), name='management-investments'),
]
