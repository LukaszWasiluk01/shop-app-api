from core.models import Category, Product
from core.permissions import IsAuthor
from rest_framework import generics, viewsets, filters
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend

from store.serializers import (CategorySerializer, ProductListSerializer,
                               ProductSerializer)
from store.filters import ProductFilter


class ProductViewSet(viewsets.ModelViewSet):
    """View for manage product object."""
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthor, ]
    authentication_classes = (TokenAuthentication, )
    filter_backends = [filters.SearchFilter, DjangoFilterBackend,
                       filters.OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'price', 'created', 'province']

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_queryset(self):
        queryset = Product.objects.all()
        return queryset

    def get_serializer_class(self):
        if self.action == 'list':
            return ProductListSerializer
        else:
            return ProductSerializer


class CategoryListAPI(generics.ListAPIView):
    """View for listing all categories."""
    model = Category
    serializer_class = CategorySerializer
    queryset = Category.objects.all()
    pagination_class = None
