import django_filters

from app.models import Housing


class HousingFilter(django_filters.FilterSet):
    price_min = django_filters.NumberFilter(field_name='price', lookup_expr='gte', label="Search price min")
    price_max = django_filters.NumberFilter(field_name='price', lookup_expr='lte', label="Search price max")
    country = django_filters.CharFilter(field_name='country', lookup_expr='iconatains', label="Search country")
    city = django_filters.CharFilter(field_name="city", lookup_expr="icontains", label="Search city")

    class Meta:
        model = Housing
        fields = ['price_min', 'price_max', 'country', 'city']
