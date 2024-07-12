from django.urls import path

from .views import (CreateClassTypesList, CreateClassColorsList, CreateClassNumberList, CreateClassCoinList,
                    CreateCoinInfoList, CreateStudentCoinList,
                    ClassColorsRetrieveUpdateDestroyAPIView, ClassNumberRetrieveUpdateDestroyAPIView,
                    ClassTypesRetrieveUpdateDestroyAPIView, ClassCoinRetrieveUpdateDestroyAPIView,
                    CoinInfoRetrieveUpdateDestroyAPIView, StudentCoinRetrieveUpdateDestroyAPIView)

urlpatterns = [
    path('class_number/', CreateClassNumberList.as_view(), name='class-number-list-create'),
    path('class_number/<int:pk>/', ClassNumberRetrieveUpdateDestroyAPIView.as_view(), name='class-number-detail'),
    path('class_colors/', CreateClassColorsList.as_view(), name='class-colors-list-create'),
    path('class_colors/<int:pk>/', ClassColorsRetrieveUpdateDestroyAPIView.as_view(), name='class-colors-detail'),
    path('class_types/', CreateClassTypesList.as_view(), name='class-types-list-create'),
    path('class_types/<int:pk>/', ClassTypesRetrieveUpdateDestroyAPIView.as_view(), name='class-types-detail'),
    path('class_coin/', CreateClassCoinList.as_view(), name='class-coin-list-create'),
    path('class_coin/<int:pk>/', ClassCoinRetrieveUpdateDestroyAPIView.as_view(), name='class-coin-detail'),
    path('coin_info/', CreateCoinInfoList.as_view(), name='coin-info-list-create'),
    path('coin_info/<int:pk>/', CoinInfoRetrieveUpdateDestroyAPIView.as_view(), name='coin-info-detail'),
    path('student_coin/', CreateStudentCoinList.as_view(), name='student-coin-list-create'),
    path('student_coin/<int:pk>/', StudentCoinRetrieveUpdateDestroyAPIView.as_view(), name='student-coin-detail'),
]
