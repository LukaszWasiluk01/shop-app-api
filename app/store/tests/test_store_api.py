from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from core.models import Product, Category
from store.serializers import ProductSerializer, CategorySerializer

PRODUCT_URL = reverse('store:products-list')
CATEGORY_URL = reverse('store:category-list')
USER_MODEL = get_user_model()


def detail_url(product_id):
    """Create and return a product detail URL."""
    return reverse('store:products-detail', args=[product_id])


def create_user(**params):
    """Create and return a new user."""
    return USER_MODEL.objects.create_user(**params)


def create_product(category, user, **params):
    """Create and return a sample product."""
    defaults = {
        'name': 'Sample name',
        'price': Decimal('5.25'),
        'description': 'Sample description',
        'province': 'Lublin',
        'phone_number': '123456789'
    }
    defaults.update(params)

    recipe = Product.objects.create(category=category, author=user, **defaults)
    return recipe


def create_category(name):
    """Create and return a sample category."""
    return Category.objects.create(name=name)


class PublicRecipeAPITests(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):

        self.user1 = create_user(
            email='testUser1@example.com',
            password='testPass123',
            username='TestUser1',
        )
        self.user2 = create_user(
            email='testUser2@example.com',
            password='testPass123',
            username='TestUser2',
        )

        self.category1 = create_category('electronics')
        self.category2 = create_category('furniture')

        self.client = APIClient()

    def test_get_product_list(self):
        """Test list and confirms there isn't author, desc and phone_number"""
        create_product(self.category1, self.user1)
        create_product(self.category2, self.user2)

        res = self.client.get(PRODUCT_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(2, len(res.data))
        self.assertNotIn('author', res.data[0])
        self.assertNotIn('desc', res.data[0])
        self.assertNotIn('phone_number', res.data[0])

    def test_get_detail_product(self):
        """Test getting details of product."""
        product = create_product(self.category1, self.user1)
        DETAIL_URL = detail_url(product.id)

        res = self.client.get(DETAIL_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        serializer = ProductSerializer(product)
        self.assertEqual(serializer.data, res.data)

    def test_post_product(self):
        """Test auth is required to make POST request."""
        res = self.client.post(PRODUCT_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_put_product(self):
        """Test auth is required to make PUT request."""
        res = self.client.post(PRODUCT_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_patch_product(self):
        """Test auth is required to make PATCH request."""
        res = self.client.post(PRODUCT_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_product(self):
        """Test auth is required to make DELETE request."""
        res = self.client.post(PRODUCT_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_category_list(self):
        """Test listing categories."""
        res = self.client.get(CATEGORY_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(2, len(res.data))

        serializer1 = CategorySerializer(self.category1)
        serializer2 = CategorySerializer(self.category2)
        self.assertIn(serializer1.data, res.data)
        self.assertIn(serializer2.data, res.data)


class PrivateUserApiTests(TestCase):
    """Test API requests that require authentication."""

    def setUp(self):
        self.category1 = create_category('electronics')
        self.category2 = create_category('furniture')

        self.user = create_user(
            email='testUser123@example.com',
            password='testPass123',
            username='TestUser',
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_post_product(self):
        """Test posting product."""

        payload = {
            'category': self.category1.name,
            'name': 'Sample name',
            'price': Decimal('5.25'),
            'description': 'Sample description',
            'province': 'Lublin',
            'phone_number': '123456789'
        }
        res = self.client.post(PRODUCT_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Product.objects.filter(author=self.user).exists())

    def test_put_product(self):
        """Test updating product via PUT request."""
        product = create_product(self.category1, self.user)

        DETAIL_URL = detail_url(product.id)
        payload = {
            'category': self.category2.name,
            'name': 'Sample name updated',
            'price': Decimal('5.25'),
            'description': 'Sample description',
            'province': 'Lublin',
            'phone_number': '123456789'
        }

        res = self.client.put(DETAIL_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        product.refresh_from_db()
        self.assertEqual(res.data['category'], payload['category'])
        self.assertEqual(res.data['name'], payload['name'])

    def test_patch_product(self):
        """Test updating product via PATCH request."""
        product = create_product(self.category1, self.user)

        DETAIL_URL = detail_url(product.id)
        payload = {
            'name': 'Sample name updated'
        }

        res = self.client.patch(DETAIL_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        product.refresh_from_db()
        self.assertEqual(res.data['name'], payload['name'])

    def test_delete_product(self):
        """Test deleting product via DELETE request."""
        product = create_product(self.category1, self.user)

        DETAIL_URL = detail_url(product.id)

        res = self.client.delete(DETAIL_URL)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Product.objects.filter(author=self.user).exists())

    def test_update_unowned_product_returns_error(self):
        """Test updating unowned product results in an error."""
        user = create_user(
            email='testUser4321@example.com',
            password='testPass4321',
            username='TestUser4321',
        )
        product = create_product(self.category1, user)

        DETAIL_URL = detail_url(product.id)
        payload = {
            'name': 'Updated name'
        }

        res = self.client.patch(DETAIL_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        product.refresh_from_db()
        self.assertNotEqual(product.name, payload['name'])

    def test_delete_unowned_product_returns_error(self):
        """Test deleting unowned product results in an error."""
        user = create_user(
            email='testUser4321@example.com',
            password='testPass4321',
            username='TestUser4321',
        )
        product = create_product(self.category1, user)

        DETAIL_URL = detail_url(product.id)

        res = self.client.delete(DETAIL_URL)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Product.objects.filter(author=user).exists())
