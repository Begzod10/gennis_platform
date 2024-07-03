from django.urls import path

from .views import (CreateLanguageList, LanguageRetrieveUpdateDestroyAPIView)

urlpatterns = [
    path('language/', CreateLanguageList.as_view(), name='language-list-create'),
    path('language/<int:pk>/', LanguageRetrieveUpdateDestroyAPIView.as_view(), name='language-detail'),
]
