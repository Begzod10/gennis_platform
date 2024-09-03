from django.urls import path

from .api.createdeleteupdate import CapitalCreateView, CapitalUpdateView, CapitalDestroyView, OldCapitalCreateView, \
    OldCapitalUpdateView, OldCapitalDestroyView
from .api.get import CapitalRetrieveAPIView, CapitalListView, OldCapitalListView, OldCapitalRetrieveAPIView, \
    CapitalRetrieveAPIViewOne
from .views import (CreateCapitalCategoryList, CapitalCategoryRetrieveUpdateDestroyAPIView)

app_name = 'Capital'

urlpatterns = [
    path('old_capital_create/', OldCapitalCreateView.as_view(), name='old-capital-create'),
    path('old_capital_update/<int:pk>/', OldCapitalUpdateView.as_view(), name='old-capital-update'),
    path('old_capital_delete/<int:pk>/', OldCapitalDestroyView.as_view(), name='old-capital-delete'),
    path('old_capital/<int:pk>/', OldCapitalRetrieveAPIView.as_view(), name='old-capital'),
    path('old_capital_list/', OldCapitalListView.as_view(), name='old-capital-list'),
    path('capital_create/', CapitalCreateView.as_view(), name='capital-create'),
    path('capital_update/<int:pk>/', CapitalUpdateView.as_view(), name='capital-update'),
    path('capital_delete/<int:pk>/', CapitalDestroyView.as_view(), name='capital-delete'),
    path('capital/<int:pk>/', CapitalRetrieveAPIView.as_view(), name='capital'),
    path('capital_one/<int:pk>/', CapitalRetrieveAPIViewOne.as_view(), name='capital'),
    path('capital_list/', CapitalListView.as_view(), name='capital-list'),
    path('capital_category/', CreateCapitalCategoryList.as_view(), name='capital-category-list-create'),
    path('capital_category/<int:pk>/', CapitalCategoryRetrieveUpdateDestroyAPIView.as_view(),
         name='capital-category-detail'),
]
