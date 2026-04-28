import django_filters
from django.db.models import Q

from user.models import UserSalaryList


class UserSalaryListFilter(django_filters.FilterSet):
    payment_type = django_filters.CharFilter(method='filter_payment_type')
    payment_sum = django_filters.RangeFilter(field_name='salary')
    date = django_filters.DateFromToRangeFilter(field_name='date')

    class Meta:
        model = UserSalaryList
        fields = ['payment_type', 'payment_sum', 'date']

    def filter_payment_type(self, queryset, name, value):
        types = value.split(',')
        q_filter = Q()
        for t in types:
            q_filter |= Q(payment_types__name__icontains=t)
        return queryset.filter(q_filter)
