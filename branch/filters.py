import django_filters
from django.db.models import Q

from branch.models import BranchLoan, BranchTransaction


class BranchTransactionFilter(django_filters.FilterSet):
    payment_type = django_filters.CharFilter(method='filter_payment_type')
    amount = django_filters.RangeFilter(field_name='amount')
    date = django_filters.DateFromToRangeFilter(field_name='date')
    direction = django_filters.CharFilter(method='filter_direction')

    class Meta:
        model = BranchTransaction
        fields = ['payment_type', 'amount', 'date', 'is_give', 'direction']

    def filter_payment_type(self, queryset, name, value):
        types = [t.strip() for t in value.split(',') if t.strip()]
        if not types:
            return queryset
        q = Q()
        for t in types:
            q |= Q(payment_type__name__icontains=t)
        return queryset.filter(q)

    def filter_direction(self, queryset, name, value):
        v = (value or '').strip().lower()
        if v == 'give':
            return queryset.filter(is_give=True)
        if v == 'receive':
            return queryset.filter(is_give=False)
        return queryset


class BranchLoanFilter(django_filters.FilterSet):
    counterparty = django_filters.NumberFilter(field_name='counterparty_id')
    issued_date = django_filters.DateFromToRangeFilter(field_name='issued_date')
    due_date = django_filters.DateFromToRangeFilter(field_name='due_date')
    principal = django_filters.RangeFilter(field_name='principal_amount')

    class Meta:
        model = BranchLoan
        fields = ['status', 'direction', 'counterparty', 'issued_date', 'due_date', 'principal']
