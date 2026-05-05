from django.urls import path

from .api.get import BranchRetrieveAPIView, BranchListAPIView, BranchForLocations, BranchListFilterAPIView, \
    BranchListAPIViewClassroom
from .api.createdeleteupdate import BranchDestroyView, BranchUpdateView, BranchCreateView
from .api.branch_transaction import (
    BranchTransactionCreateView,
    BranchTransactionDeletedListView,
    BranchTransactionDeleteView,
    BranchTransactionListView,
    BranchTransactionMonthListView,
    BranchTransactionUpdateView,
)
from .api.branch_loan import (
    BranchLoanCancelView,
    BranchLoanCreateView,
    BranchLoanDetailView,
    BranchLoanListView,
    BranchLoanOutstandingView,
    BranchLoanRepayView,
    BranchLoanUpdateView,
)

urlpatterns = [
    path('branch_create/', BranchCreateView.as_view(), name='branch-create'),
    path('branch_update/<int:pk>/', BranchUpdateView.as_view(), name='branch-update'),
    path('branch_delete/<int:pk>/', BranchDestroyView.as_view(), name='branch-delete'),
    path('branch/<int:pk>/', BranchRetrieveAPIView.as_view(), name='branch'),
    path('branch_list/', BranchListAPIView.as_view(), name='branch-list'),
    path('branch_list-classroom/', BranchListAPIViewClassroom.as_view(), name='branch-list'),
    path('branch_for_locations/', BranchForLocations.as_view(), name='branch_for_locations'),
    path('branch_filtered/', BranchListFilterAPIView.as_view(), name='branch-filtered'),

    path('branch_transactions/', BranchTransactionListView.as_view(), name='branch-transaction-list'),
    path('branch_transaction/', BranchTransactionCreateView.as_view(), name='branch-transaction-create'),
    path('branch_transaction/<int:month>/<int:year>/', BranchTransactionMonthListView.as_view(),
         name='branch-transaction-month-list'),
    path('branch_transaction/<int:pk>/update/', BranchTransactionUpdateView.as_view(),
         name='branch-transaction-update'),
    path('branch_transaction/<int:pk>/delete/', BranchTransactionDeleteView.as_view(),
         name='branch-transaction-delete'),
    path('branch_transaction/deleted/<int:month>/<int:year>/', BranchTransactionDeletedListView.as_view(),
         name='branch-transaction-deleted-list'),

    path('branch_loans/', BranchLoanListView.as_view(), name='branch-loan-list'),
    path('branch_loans/outstanding/', BranchLoanOutstandingView.as_view(), name='branch-loan-outstanding'),
    path('branch_loans/create/', BranchLoanCreateView.as_view(), name='branch-loan-create'),
    path('branch_loans/<int:pk>/', BranchLoanDetailView.as_view(), name='branch-loan-detail'),
    path('branch_loans/<int:pk>/update/', BranchLoanUpdateView.as_view(), name='branch-loan-update'),
    path('branch_loans/<int:pk>/repay/', BranchLoanRepayView.as_view(), name='branch-loan-repay'),
    path('branch_loans/<int:pk>/cancel/', BranchLoanCancelView.as_view(), name='branch-loan-cancel'),
]
