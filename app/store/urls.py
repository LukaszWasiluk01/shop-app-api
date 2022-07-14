from django.urls import include, path
from rest_framework.routers import DefaultRouter

from store.views import CategoryListAPI, ProductViewSet

app_name = 'store'

router = DefaultRouter()
router.register('products', ProductViewSet, basename='products')

urlpatterns = [
    path('', include(router.urls)),
    path('categories/', CategoryListAPI.as_view(), name='category-list'),
]
