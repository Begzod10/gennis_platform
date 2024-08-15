from django.urls import path

from .views import TransferCollectedBookPaymentsCreateView, TransferBookOrderCreateView, \
    TransferCenterBalanceCreateView, TransferBalanceOverheadCreateView, TransferEditorBalanceCreateView, \
    TransferBranchPaymentCreateView, TransferUserBookCreateView

urlpatterns = [
    path('create_collected_book_payment/', TransferCollectedBookPaymentsCreateView.as_view(),
         name='create-collected-book-payment'),
    path('create_book_ordert/', TransferBookOrderCreateView.as_view(),
         name='create-book-order'),
    path('create_center_balance/', TransferCenterBalanceCreateView.as_view(),
         name='create-center-balance'),
    path('create_balance_overhead/', TransferBalanceOverheadCreateView.as_view(),
         name='create-balance-overhead'),
    path('create_editor_balance/', TransferEditorBalanceCreateView.as_view(),
         name='create-editor-balance'),
    path('create_branch_payment/', TransferBranchPaymentCreateView.as_view(),
         name='create-branch-payment'),
    path('create_user_book/', TransferUserBookCreateView.as_view(),
         name='create-user-book'),
]
