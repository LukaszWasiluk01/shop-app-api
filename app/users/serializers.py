from django.contrib.auth import get_user_model

from rest_framework import serializers


class BaseUserSerializer(serializers.ModelSerializer):
    """Base serializer for user object."""

    class Meta:
        model = get_user_model()


class UserSerializer(BaseUserSerializer):
    """Serializer for receiving user object."""

    class Meta(BaseUserSerializer.Meta):
        fields = ('email', 'username', 'date_joined', 'last_login', 'password')
        read_only_fields = ('username', 'date_joined', 'last_login')
        extra_kwargs = {'password': {'write_only': True, 'min_length': 5}}

    def update(self, instance, validated_data):
        """Update and return user."""
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()

        return user


class RegisterUserSerializer(BaseUserSerializer):
    """Serializer for registering user."""

    class Meta(BaseUserSerializer.Meta):
        fields = ('email', 'username', 'password')
        extra_kwargs = {'password': {'write_only': True, 'min_length': 5}}

    def create(self, validated_data):
        """Create and return a user with encrypted password."""
        return get_user_model().objects.create_user(**validated_data)
