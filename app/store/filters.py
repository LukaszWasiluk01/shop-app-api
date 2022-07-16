from django_filters import rest_framework as filters
from core.models import Product


class ProductFilter(filters.FilterSet):
    class Meta:
        model = Product
        fields = {
            'category__name': ['exact'],
            'price': ['gt', 'lt'],
            'created': ['gt', 'lt'],
        }
