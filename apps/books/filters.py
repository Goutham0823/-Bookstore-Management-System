import django_filters
from .models import Book


class BookFilter(django_filters.FilterSet):
    """Filter set for searching and filtering books."""
    title = django_filters.CharFilter(lookup_expr='icontains', label='Title contains')
    author = django_filters.CharFilter(lookup_expr='icontains', label='Author contains')
    genre = django_filters.CharFilter(lookup_expr='iexact', label='Genre (exact, case-insensitive)')
    min_price = django_filters.NumberFilter(field_name='price', lookup_expr='gte', label='Min price')
    max_price = django_filters.NumberFilter(field_name='price', lookup_expr='lte', label='Max price')
    in_stock = django_filters.BooleanFilter(method='filter_in_stock', label='In stock only')

    def filter_in_stock(self, queryset, name, value):
        if value:
            return queryset.filter(stock_quantity__gt=0)
        return queryset.filter(stock_quantity=0)

    class Meta:
        model = Book
        fields = ['title', 'author', 'genre', 'min_price', 'max_price', 'in_stock']
