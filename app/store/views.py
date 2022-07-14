from core.models import Category, Product
from core.permissions import IsAuthor
from rest_framework import generics, viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from store.serializers import (CategorySerializer, ProductListSerializer,
                               ProductSerializer)


class ProductViewSet(viewsets.ModelViewSet):
    """View for manage product object."""
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthor, ]
    authentication_classes = (TokenAuthentication, )

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
