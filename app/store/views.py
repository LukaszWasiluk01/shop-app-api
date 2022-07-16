from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import filters, generics, status, viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from core.models import Category, Product
from core.permissions import IsAuthor
from store.filters import ProductFilter
from store.serializers import (CategorySerializer, ProductListSerializer,
                               ProductSerializer, ProductImageSerializer)


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
        elif self.action == 'upload_image':
            return ProductImageSerializer
        else:
            return ProductSerializer

    @action(methods=['POST'], detail=True, url_path='upload-image')
    def upload_image(self, request, pk=None):
        """Upload an image to product."""
        product = self.get_object()
        serializer = self.get_serializer(product, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CategoryListAPI(generics.ListAPIView):
    """View for listing all categories."""
    model = Category
    serializer_class = CategorySerializer
    queryset = Category.objects.all()
    pagination_class = None
