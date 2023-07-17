from rest_framework import generics
from users.serializers import RegisterUserSerializer


class RegisterUserView(generics.CreateAPIView):
    """Create a new user in the system."""

    serializer_class = RegisterUserSerializer
