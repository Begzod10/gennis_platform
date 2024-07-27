from django.urls import path

from .views import (CreateClassTypesList, CreateClassColorsList,
                    ClassColorsRetrieveUpdateDestroyAPIView,
                    ClassTypesRetrieveUpdateDestroyAPIView, )
from .api.get import ClassNumberRetrieveAPIView, ClassCoinRetrieveAPIView, CoinInfoRetrieveAPIView, \
    StudentCoinRetrieveAPIView, StudentCoinListView, ClassCoinListView, ClassNumberListView, CoinInfoListView
from .api.createdeleteupdate import CoinInfoCreateView, CoinInfoDestroyView, CoinInfoUpdateView, StudentCoinDestroyView, \
    ClassCoinCreateView, ClassCoinDestroyView, ClassNumberDestroyView, ClassCoinUpdateView, StudentCoinCreateView, \
    StudentCoinUpdateView, ClassNumberCreateView, ClassNumberUpdateView

urlpatterns = [
    path('coin_info_create/', CoinInfoCreateView.as_view(), name='coin-info-create'),
    path('coin_info_update/<int:pk>/', CoinInfoUpdateView.as_view(), name='coin-info-update'),
    path('coin_info_delete/<int:pk>/', CoinInfoDestroyView.as_view(), name='coin-info-delete'),
    path('coin_info/<int:pk>/', CoinInfoRetrieveAPIView.as_view(), name='coin-info'),
    path('coin_info_list/', CoinInfoListView.as_view(), name='coin-info-list'),
    path('class_coin_create/', ClassCoinCreateView.as_view(), name='class-coin-create'),
    path('class_coin_update/<int:pk>/', ClassCoinUpdateView.as_view(), name='class-coin-update'),
    path('class_coin_delete/<int:pk>/', ClassCoinDestroyView.as_view(), name='class-coin-delete'),
    path('class_coin/<int:pk>/', ClassCoinRetrieveAPIView.as_view(), name='class-coin'),
    path('class_coin_list/', ClassCoinListView.as_view(), name='class-coin-list'),
    path('student_coin_create/', StudentCoinCreateView.as_view(), name='student-coin-create'),
    path('student_coin_update/<int:pk>/', StudentCoinUpdateView.as_view(), name='student-coin-update'),
    path('student_coin_delete/<int:pk>/', StudentCoinDestroyView.as_view(), name='student-coin-delete'),
    path('student_coin/<int:pk>/', StudentCoinRetrieveAPIView.as_view(), name='student-coin'),
    path('student_coin_list/', StudentCoinListView.as_view(), name='student-coin-list'),
    path('class_number_create/', ClassNumberCreateView.as_view(), name='class-number-create'),
    path('class_number_update/<int:pk>/', ClassNumberUpdateView.as_view(), name='class-number-update'),
    path('class_number_delete/<int:pk>/', ClassNumberDestroyView.as_view(), name='class-number-delete'),
    path('class_number/<int:pk>/', ClassNumberRetrieveAPIView.as_view(), name='class-number'),
    path('class_number_list/', ClassNumberListView.as_view(), name='class-number-list'),
    path('class_colors/', CreateClassColorsList.as_view(), name='class-colors-list-create'),
    path('class_colors/<int:pk>/', ClassColorsRetrieveUpdateDestroyAPIView.as_view(), name='class-colors-detail'),
    path('class_types/', CreateClassTypesList.as_view(), name='class-types-list-create'),
    path('class_types/<int:pk>/', ClassTypesRetrieveUpdateDestroyAPIView.as_view(), name='class-types-detail'),
]
