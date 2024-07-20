from django.urls import path

from .views import (
    BookListCreateView,
    BookRetrieveUpdateDestroyView,
    BookImageListCreateView,
    BookImageRetrieveUpdateDestroyView,
    BookOrderListCreateView,
    BookOrderRetrieveUpdateDestroyView,
    CollectedBookPaymentsRetrieveUpdateDestroyView,
    BalanceOverheadListCreateView,
    BalanceOverheadRetrieveUpdateDestroyView
)

urlpatterns = [
    path('collected_book_payments/<int:pk>/', CollectedBookPaymentsRetrieveUpdateDestroyView.as_view(),
         name='collected-book-payments-retrieve-update-destroy'),
    path('book_order/', BookOrderListCreateView.as_view(), name='book-order-list-create'),
    path('book_order/<int:pk>/', BookOrderRetrieveUpdateDestroyView.as_view(),
         name='book-order-retrieve-update-destroy'),
    path('books/', BookListCreateView.as_view(), name='book-list-create'),
    path('books/<int:pk>/', BookRetrieveUpdateDestroyView.as_view(), name='book-retrieve-update-destroy'),
    path('book_images/', BookImageListCreateView.as_view(), name='book-image-list-create'),
    path('book_images/<int:pk>/', BookImageRetrieveUpdateDestroyView.as_view(),
         name='book-image-retrieve-update-destroy'),
    path('balance_overhead/', BalanceOverheadListCreateView.as_view(), name='balance-overhead-list-create'),
    path('balance_overhead/<int:pk>/', BalanceOverheadRetrieveUpdateDestroyView.as_view(),
         name='balance-overhead-retrieve-update-destroy'),
]
