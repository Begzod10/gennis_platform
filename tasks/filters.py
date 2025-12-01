# filters.py

import django_filters
from tasks.models import Mission


class MissionFilter(django_filters.FilterSet):
    created_at = django_filters.DateFromToRangeFilter()
    status = django_filters.CharFilter(lookup_expr="iexact")
    creator = django_filters.NumberFilter(field_name="creator__id")
    executor = django_filters.NumberFilter(field_name="executor__id")
    reviewer = django_filters.NumberFilter(field_name="reviewer__id")
    deadline = django_filters.DateFromToRangeFilter()

    class Meta:
        model = Mission
        fields = ["status", "creator", "executor", "reviewer", "created_at", "deadline"]
