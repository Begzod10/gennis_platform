import django_filters

from students.models import Student


class StudentFilter(django_filters.FilterSet):
    branch = django_filters.NumberFilter(field_name='user__branch')

    class Meta:
        model = Student
        fields = ['branch']