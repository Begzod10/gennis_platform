from django.urls import path

from .views import (
    BookListCreateView,
    BookRetrieveUpdateDestroyView,
    BookImageListCreateView,
    BookImageRetrieveUpdateDestroyView,
    BookOrderListCreateView,
    BookOrderRetrieveUpdateDestroyView
)

urlpatterns = [
    path('book_order/', BookOrderListCreateView.as_view(), name='book-order-list-create'),
    path('book_order/<int:pk>/', BookOrderRetrieveUpdateDestroyView.as_view(),
         name='book-order-retrieve-update-destroy'),
    path('books/', BookListCreateView.as_view(), name='book-list-create'),
    path('books/<int:pk>/', BookRetrieveUpdateDestroyView.as_view(), name='book-retrieve-update-destroy'),
    path('book-images/', BookImageListCreateView.as_view(), name='book-image-list-create'),
    path('book-images/<int:pk>/', BookImageRetrieveUpdateDestroyView.as_view(),
         name='book-image-retrieve-update-destroy'),
]
