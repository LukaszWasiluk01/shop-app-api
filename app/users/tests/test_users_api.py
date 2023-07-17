from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

CREATE_USER_URL = reverse("users:register")
USER_URL_ME = reverse("users:rest_user_details")
USER_MODEL = get_user_model()


def create_user(**params):
    """Create and return a new user."""
    return USER_MODEL.objects.create_user(**params)


class PublicUserApiTests(TestCase):
    """Test the public features of the user API."""

    def setUp(self):
        self.client = APIClient()

    def test_create_user(self):
        """Test creating a user is successful."""

        payload = {"email": "user123@example.com", "username": "user123", "password": "StrongPassword123"}
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = USER_MODEL.objects.get(email=payload["email"])
        self.assertTrue(user.check_password(payload["password"]))
        self.assertNotIn("password", res.data)

    def test_unique_username(self):
        """Test if error is returned if user with username exists"""

        payload = {"email": "user123@example.com", "username": "user123", "password": "StrongPassword123"}
        create_user(**payload)

        payload["email"] = "user1234@example.com"
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unique_email(self):
        """Test if error is returned if user with email exists"""

        payload = {"email": "user123@example.com", "username": "user123", "password": "StrongPassword123"}
        create_user(**payload)

        payload["username"] = "user1234"
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_user_unauthorized(self):
        """Test authentication is required for users."""
        res = self.client.get(USER_URL_ME)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserApiTests(TestCase):
    """Test API requests that require authentication."""

    def setUp(self):
        self.user = create_user(
            email="testUser123@example.com",
            password="testPass123",
            username="TestUser",
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_get_user(self):
        res = self.client.get(USER_URL_ME)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["username"], self.user.username)
        self.assertEqual(res.data["email"], self.user.email)
        self.assertIn("date_joined", res.data)
        self.assertIn("last_login", res.data)
        self.assertNotIn("password", res.data)

    def test_put_update(self):
        """Test put method on user object and that username is not editable."""

        payload = {"email": "user123@example.com", "password": "StrongPassword123"}
        res = self.client.put(USER_URL_ME, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, payload["email"])
        self.assertTrue(self.user.check_password(payload["password"]))

    def test_patch_email_error_update(self):
        """Test updating with existing email"""

        create_user(
            email="testUser@example.com",
            password="testPass123",
            username="TestUser1234",
        )

        payload = {
            "email": "testUser@example.com",
        }
        res = self.client.patch(USER_URL_ME, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.user.refresh_from_db()
        self.assertNotEqual(self.user.email, payload["email"])

    def test_post_me_not_allowed(self):
        """Test POST is not allowed for the me endpoint."""
        res = self.client.post(USER_URL_ME, {})

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
