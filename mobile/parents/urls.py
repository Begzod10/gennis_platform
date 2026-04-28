# parents/urls.py
from django.urls import path
from mobile.parents.views import ChildrenListView, ChildrenDebtMonthView, ChildrenTodayTimeTableView, \
    ChildrenAttendanceMonthView, ListTermChildren, TermsByChildren

urlpatterns = [
    path('children/', ChildrenListView.as_view(), name='children-list'),
    path("children-month-debts/", ChildrenDebtMonthView.as_view(), name='children-month-debts'),
    path("children-time-table/", ChildrenTodayTimeTableView.as_view(), name='children-time-table'),
    path('children-attendance/', ChildrenAttendanceMonthView.as_view(), name='children-attendance'),
    path("children-terms-list/", ListTermChildren.as_view(), name='children-terms-list'),
    path('children-term/', TermsByChildren.as_view(), name='children-term'),
]
