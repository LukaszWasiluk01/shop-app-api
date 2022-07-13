from rest_framework import generics
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from users.serializers import RegisterUserSerializer, UserSerializer


class RegisterUserView(generics.CreateAPIView):
    """Create a new user in the system."""
    serializer_class = RegisterUserSerializer


class ManageUserView(generics.RetrieveUpdateDestroyAPIView):
    """Manage the authenticated user."""
    serializer_class = UserSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_object(self):
        """Retrieve and return the authenticated user."""
        return self.request.user
