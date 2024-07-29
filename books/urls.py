from django.urls import path

from .views import (
    BookListCreateView,
    BookRetrieveUpdateDestroyView,
    BookImageListCreateView,
    BookImageRetrieveUpdateDestroyView,
)
from .api.get import BookOrderListView, BookOrderRetrieveView, CollectedBookPaymentsRetrieveView, \
    BookOverheadRetrieveView, BookOverheadListView, BalanceOverheadListView, BalanceOverheadRetrieveView, \
    CenterBalanceListView, CenterBalanceRetrieveView, BranchPaymentListView, BranchPaymentRetrieveView, \
    EditorBalanceListView, EditorBalanceRetrieveView
from .api.createdeleteupdate import BookOrderDestroyView, BookOrderCreateView, BookOrderUpdateView, \
    CollectedBookPaymentsUpdateView, BookOverheadUpdateView, BalanceOverheadUpdateView, BalanceOverheadCreateView, \
    BookOverheadDestroyView, BookOverheadCreateView, BalanceOverheadDestroyView

urlpatterns = [
    path('editor_balance/<int:pk>/', EditorBalanceRetrieveView.as_view(), name='editor-balance'),
    path('editor_balance_list/', EditorBalanceListView.as_view(), name='editor-balance-list'),
    path('branch_payment/<int:pk>/', BranchPaymentRetrieveView.as_view(), name='branch-payment'),
    path('branch_payment_list/', BranchPaymentListView.as_view(), name='branch-payment-list'),
    path('center_balance/<int:pk>/', CenterBalanceRetrieveView.as_view(), name='center-balance'),
    path('center_balance_list/', CenterBalanceListView.as_view(), name='center-balance-list'),
    path('book_overhead_create/', BookOverheadCreateView.as_view(), name='book-overhead-create'),
    path('book_overhead_update/<int:pk>/', BookOverheadUpdateView.as_view(), name='book-overhead-update'),
    path('book_overhead_delete/<int:pk>/', BookOverheadDestroyView.as_view(), name='book-overhead-delete'),
    path('book_overhead/<int:pk>/', BookOverheadRetrieveView.as_view(), name='book-overhead'),
    path('book_overhead_list/', BookOverheadListView.as_view(), name='book-overhead-list'),
    path('balance_overhead_create/', BalanceOverheadCreateView.as_view(), name='balance-overhead-create'),
    path('balance_overhead_update/<int:pk>/', BalanceOverheadUpdateView.as_view(), name='balance-overhead-update'),
    path('balance_overhead_delete/<int:pk>/', BalanceOverheadDestroyView.as_view(), name='balance-overhead-delete'),
    path('balance_overhead/<int:pk>/', BalanceOverheadRetrieveView.as_view(), name='balance-overhead'),
    path('balance_overhead_list/', BalanceOverheadListView.as_view(), name='balance-overhead-list'),
    path('book_order_create/', BookOrderCreateView.as_view(), name='book-order-create'),
    path('book_order_update/<int:pk>/', BookOrderUpdateView.as_view(), name='book-order-update'),
    path('book_order_delete/<int:pk>/', BookOrderDestroyView.as_view(), name='book-order-delete'),
    path('book_order/<int:pk>/', BookOrderRetrieveView.as_view(), name='book-order'),
    path('book_order_list/', BookOrderListView.as_view(), name='book-order-list'),
    path('collected_book_payments_update/<int:pk>/', CollectedBookPaymentsUpdateView.as_view(),
         name='collected-book-payments-update'),
    path('collected_book_payments/<int:pk>/', CollectedBookPaymentsRetrieveView.as_view(),
         name='collected-book-payments'),
    path('books/', BookListCreateView.as_view(), name='book-list-create'),
    path('books/<int:pk>/', BookRetrieveUpdateDestroyView.as_view(), name='book-retrieve-update-destroy'),
    path('book_images/', BookImageListCreateView.as_view(), name='book-image-list-create'),
    path('book_images/<int:pk>/', BookImageRetrieveUpdateDestroyView.as_view(),
         name='book-image-retrieve-update-destroy'),
]
