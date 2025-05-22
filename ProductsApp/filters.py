import django_filters
from django.db.models import Q
from .models import Products, Categories
from django.utils import timezone
from datetime import timedelta

class ProductFilters(django_filters.FilterSet):
    # Text Search Filters
    name = django_filters.CharFilter(lookup_expr='iexact')
    keyword = django_filters.CharFilter(method='filter_keyword')
    description = django_filters.CharFilter(lookup_expr='icontains')
    
    # Price Filters
    min_price = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name='price', lookup_expr='lte')
    
    # Category and Brand Filters
    categories = django_filters.MultipleChoiceFilter(
        field_name='category',
        choices=Categories.choices
    )
    brands = django_filters.CharFilter(method='filter_brands')
    
    # Rating Filters
    min_rating = django_filters.NumberFilter(field_name='rating', lookup_expr='gte')
    max_rating = django_filters.NumberFilter(field_name='rating', lookup_expr='lte')
    
    # Review Count Filter
    min_reviews = django_filters.NumberFilter(field_name='review_count', lookup_expr='gte')
    
    # Stock Status
    in_stock = django_filters.BooleanFilter(method='filter_stock')
    
    # Date Filters
    new_arrivals = django_filters.BooleanFilter(method='filter_new_arrivals')
    
    # Sort Options
    sort_by = django_filters.CharFilter(method='apply_sorting')

    class Meta:
        model = Products
        fields = [
            'name', 'keyword', 'description', 
            'min_price', 'max_price', 
            'categories', 'brands',
            'min_rating', 'max_rating',
            'min_reviews', 'in_stock',
            'new_arrivals', 'sort_by'
        ]

    def filter_keyword(self, queryset, name, value):
        """Search in name, description, and brand"""
        return queryset.filter(
            Q(name__icontains=value) |
            Q(description__icontains=value) |
            Q(brand__icontains=value)
        )

    def filter_brands(self, queryset, name, value):
        """Filter by multiple brands (comma-separated)"""
        if value:
            brands = [brand.strip() for brand in value.split(',')]
            return queryset.filter(brand__in=brands)
        return queryset

    def filter_stock(self, queryset, name, value):
        """Filter in-stock products"""
        if value is True:
            return queryset.filter(stock__gt=0)
        return queryset

    def filter_new_arrivals(self, queryset, name, value):
        """Filter products added in the last 30 days"""
        if value is True:
            thirty_days_ago = timezone.now() - timedelta(days=30)
            return queryset.filter(created_at__gte=thirty_days_ago)
        return queryset

    def apply_sorting(self, queryset, name, value):
        """Apply sorting based on different criteria"""
        sorting_options = {
            'price_asc': 'price',
            'price_desc': '-price',
            'rating_desc': '-rating',
            'newest': '-created_at',
            'reviews': '-review_count',
        }
        
        order_by = sorting_options.get(value, 'name')  # Default sort by name
        return queryset.order_by(order_by)