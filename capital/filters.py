import django_filters
from django.db.models import Q
from .models import OldCapital


class OldCapitalFilter(django_filters.FilterSet):
    payment_type = django_filters.CharFilter(method='filter_payment_type')
    payment_sum = django_filters.RangeFilter(field_name='price')
    date = django_filters.DateFromToRangeFilter(field_name='added_date')
    class Meta:
        model = OldCapital
        fields = ['payment_type', 'payment_sum','date']

    def filter_payment_type(self, queryset, name, value):
        types = value.split(',')
        q_filter = Q()
        for t in types:
            q_filter |= Q(payment_type__name__icontains=t)
        return queryset.filter(q_filter)
