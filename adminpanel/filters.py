import django_filters
from django_filters import DateFilter
from src.models import RegisterUser


class UserFilter(django_filters.FilterSet):
    from_date = DateFilter(field_name='created_at', lookup_expr='gte', label='From Date')
    to_date = DateFilter(field_name='created_at', lookup_expr='lte', label='To Date')

    class Meta:
        model = RegisterUser
        fields = ('from_date', 'to_date')
