from django.urls import path

from .views import (CreateCapitalCategoryList, CapitalCategoryRetrieveUpdateDestroyAPIView)
from .api.get import CapitalRetrieveAPIView, CapitalListView
from .api.createdeleteupdate import CapitalCreateView, CapitalUpdateView, CapitalDestroyView

urlpatterns = [
    path('capital_create/', CapitalCreateView.as_view(), name='capital-create'),
    path('capital_update/<int:pk>/', CapitalUpdateView.as_view(), name='capital-update'),
    path('capital_delete/<int:pk>/', CapitalDestroyView.as_view(), name='capital-delete'),
    path('capital/<int:pk>/', CapitalRetrieveAPIView.as_view(), name='capital'),
    path('capital_list/', CapitalListView.as_view(), name='capital-list'),
    path('capital_category/', CreateCapitalCategoryList.as_view(), name='capital-category-list-create'),
    path('capital_category/<int:pk>/', CapitalCategoryRetrieveUpdateDestroyAPIView.as_view(),
         name='capital-category-detail'),
]
