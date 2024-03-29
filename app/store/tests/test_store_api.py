import os
import tempfile
from decimal import Decimal

from core.models import Category, Product
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from PIL import Image
from rest_framework import status
from rest_framework.test import APIClient
from store.serializers import CategorySerializer, ProductListSerializer, ProductSerializer

PRODUCT_URL = reverse("store:products-list")
MY_PRODUCTS_URL = reverse("store:products-my-products")
CATEGORY_URL = reverse("store:category-list")
USER_MODEL = get_user_model()


def detail_url(product_id):
    """Create and return a product detail URL."""
    return reverse("store:products-detail", args=[product_id])


def image_upload_url(product_id):
    """Create and return an image upload URL."""
    return reverse("store:products-upload-image", args=[product_id])


def create_user(**params):
    """Create and return a new user."""
    return USER_MODEL.objects.create_user(**params)


def create_product(category, user, **params):
    """Create and return a sample product."""
    defaults = {
        "name": "Sample name",
        "price": Decimal("5.25"),
        "description": "Sample description",
        "province": "Lublin",
        "phone_number": "123456789",
    }
    defaults.update(params)

    product = Product.objects.create(category=category, author=user, **defaults)

    return product


def create_category(name):
    """Create and return a sample category."""
    return Category.objects.create(name=name)


class PublicProductAPITests(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):
        self.user1 = create_user(
            email="testUser1@example.com",
            password="testPass123",
            username="TestUser1",
        )
        self.user2 = create_user(
            email="testUser2@example.com",
            password="testPass123",
            username="TestUser2",
        )

        self.category1 = create_category("electronics")
        self.category2 = create_category("furniture")

        self.client = APIClient()

    def test_get_product_list(self):
        """Test list and confirms there isn't author, desc and phone_number"""
        create_product(self.category1, self.user1)
        create_product(self.category2, self.user2)

        res = self.client.get(PRODUCT_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(2, len(res.data["results"]))
        self.assertNotIn("author", res.data["results"][0])
        self.assertNotIn("desc", res.data["results"][0])
        self.assertNotIn("phone_number", res.data["results"][0])

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

    def test_product_list_pagination(self):
        """Test product list pagination."""
        for _ in range(9):
            create_product(self.category1, self.user1)

        res = self.client.get(PRODUCT_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(8, len(res.data["results"]))

        params = {"page": 2}
        res = self.client.get(PRODUCT_URL, params)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(1, len(res.data["results"]))

    def test_product_list_search_filtering(self):
        """Test product list search filtering"""
        p1 = create_product(self.category1, self.user1, name="A test")
        create_product(self.category2, self.user2, name="B sample")
        p3 = create_product(self.category2, self.user2, description="Test sample")

        params = {"search": "test"}

        res = self.client.get(PRODUCT_URL, params)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        s1 = ProductListSerializer(p1)
        s3 = ProductListSerializer(p3)
        self.assertEqual(2, len(res.data["results"]))
        self.assertIn(s1.data, res.data["results"])
        self.assertIn(s3.data, res.data["results"])

    def test_product_list_order_filtering(self):
        """Test product list order filtering"""
        p1 = create_product(self.category1, self.user1, price="1.25")
        p2 = create_product(self.category2, self.user2, price="2.25")
        p3 = create_product(self.category2, self.user2, price="3.25")

        params = {"ordering": "-price"}

        res = self.client.get(PRODUCT_URL, params)

        s1 = ProductListSerializer(p1)
        s2 = ProductListSerializer(p2)
        s3 = ProductListSerializer(p3)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(s3.data, res.data["results"][0])
        self.assertEqual(s2.data, res.data["results"][1])
        self.assertEqual(s1.data, res.data["results"][2])

    def test_product_list_detail_data_filtering(self):
        """Test product list detail data filtering"""
        create_product(self.category1, self.user1, price="1.25")
        p2 = create_product(self.category1, self.user2, price="2.25")
        create_product(self.category2, self.user2, price="3.25")

        params = {"price__gt": 2, "price__lt": 4, "category__name": self.category1.name}

        res = self.client.get(PRODUCT_URL, params)

        s2 = ProductListSerializer(p2)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(1, len(res.data["results"]))
        self.assertEqual(s2.data, res.data["results"][0])


class PrivateUserApiTests(TestCase):
    """Test API requests that require authentication."""

    def setUp(self):
        self.category1 = create_category("electronics")
        self.category2 = create_category("furniture")

        self.user = create_user(
            email="testUser123@example.com",
            password="testPass123",
            username="TestUser",
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_post_product(self):
        """Test posting product."""

        payload = {
            "category": self.category1.name,
            "name": "Sample name",
            "price": Decimal("5.25"),
            "description": "Sample description",
            "province": "Lublin",
            "phone_number": "123456789",
        }
        res = self.client.post(PRODUCT_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Product.objects.filter(author=self.user).exists())

    def test_put_product(self):
        """Test updating product via PUT request."""
        product = create_product(self.category1, self.user)

        DETAIL_URL = detail_url(product.id)
        payload = {
            "category": self.category2.name,
            "name": "Sample name updated",
            "price": Decimal("5.25"),
            "description": "Sample description",
            "province": "Lublin",
            "phone_number": "123456789",
        }

        res = self.client.put(DETAIL_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        product.refresh_from_db()
        self.assertEqual(res.data["category"], payload["category"])
        self.assertEqual(res.data["name"], payload["name"])

    def test_patch_product(self):
        """Test updating product via PATCH request."""
        product = create_product(self.category1, self.user)

        DETAIL_URL = detail_url(product.id)
        payload = {"name": "Sample name updated"}

        res = self.client.patch(DETAIL_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        product.refresh_from_db()
        self.assertEqual(res.data["name"], payload["name"])

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
            email="testUser4321@example.com",
            password="testPass4321",
            username="TestUser4321",
        )
        product = create_product(self.category1, user)

        DETAIL_URL = detail_url(product.id)
        payload = {"name": "Updated name"}

        res = self.client.patch(DETAIL_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        product.refresh_from_db()
        self.assertNotEqual(product.name, payload["name"])

    def test_delete_unowned_product_returns_error(self):
        """Test deleting unowned product results in an error."""
        user = create_user(
            email="testUser4321@example.com",
            password="testPass4321",
            username="TestUser4321",
        )
        product = create_product(self.category1, user)

        DETAIL_URL = detail_url(product.id)

        res = self.client.delete(DETAIL_URL)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Product.objects.filter(author=user).exists())

    def test_my_product_listing_owned_products(self):
        """Test receiving list of only owned products."""
        user = create_user(
            email="testUser4321@example.com",
            password="testPass4321",
            username="TestUser4321",
        )
        create_product(self.category1, user)
        create_product(self.category2, self.user)

        res = self.client.get(MY_PRODUCTS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(1, len(res.data["results"]))
        self.assertEqual(self.category2.name, res.data["results"][0]["category"])


class ImageUploadTests(TestCase):
    """Tests for the image upload API."""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "user123@example.com",
            "StrongPassword123",
        )
        self.client.force_authenticate(self.user)

        self.category = create_category("electronics")
        self.product = create_product(self.category, self.user)

    def tearDown(self):
        self.product.image.delete()

    def test_upload_image(self):
        """Test uploading an image to a product."""
        url = image_upload_url(self.product.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as image_file:
            img = Image.new("RGB", (10, 10))
            img.save(image_file, format="JPEG")
            image_file.seek(0)
            payload = {"image": image_file}
            res = self.client.post(url, payload, format="multipart")

        self.product.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("image", res.data)
        self.assertTrue(os.path.exists(self.product.image.path))

    def test_upload_image_bad_request(self):
        """Test uploading an invalid image."""
        url = image_upload_url(self.product.id)
        payload = {"image": "notanimage"}
        res = self.client.post(url, payload, format="multipart")

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
