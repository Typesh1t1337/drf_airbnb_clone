import django_filters

from app.models import Housing


class HousingFilter(django_filters.FilterSet):
    price_min = django_filters.NumberFilter(field_name='price', lookup_expr='gte', label="Search price min")
    price_max = django_filters.NumberFilter(field_name='price', lookup_expr='lte', label="Search price max")
    search = django_filters.CharFilter(field_name='name', lookup_expr='icontains', label="Search by name")
    city = django_filters.CharFilter(field_name="city", lookup_expr="icontains", label="Search city")
    type = django_filters.CharFilter(field_name="type__name", lookup_expr="exact", label="Search type")
    owner = django_filters.CharFilter(field_name="owner__username", lookup_expr="exact", label="Search owner")

    class Meta:
        model = Housing
        fields = ['price_min', 'price_max', 'country', 'city', "search", "type"]
