from django.urls import path

from .views import (CreateClassTypesList, CreateClassColorsList, CreateClassNumberList,
                    ClassColorsRetrieveUpdateDestroyAPIView, ClassNumberRetrieveUpdateDestroyAPIView,
                    ClassTypesRetrieveUpdateDestroyAPIView)

urlpatterns = [
    path('class_number/', CreateClassNumberList.as_view(), name='class-number-list-create'),
    path('class_number/<int:pk>/', ClassNumberRetrieveUpdateDestroyAPIView.as_view(), name='class-number-detail'),
    path('class_colors/', CreateClassColorsList.as_view(), name='class-colors-list-create'),
    path('class_colors/<int:pk>/', ClassColorsRetrieveUpdateDestroyAPIView.as_view(), name='class-colors-detail'),
    path('class_types/', CreateClassTypesList.as_view(), name='class-class-list-create'),
    path('class_types/<int:pk>/', ClassTypesRetrieveUpdateDestroyAPIView.as_view(), name='class-types-detail'),
]
