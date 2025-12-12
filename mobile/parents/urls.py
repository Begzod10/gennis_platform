# parents/urls.py
from django.urls import path
from mobile.parents.views import ChildrenListView

urlpatterns = [
    path('children/', ChildrenListView.as_view(), name='children-list'),
]
