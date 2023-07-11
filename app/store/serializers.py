from core.models import Category, Product
from django.contrib.auth import get_user_model
from rest_framework import serializers

UserModel = get_user_model()


class UserProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = ("id", "username", "date_joined", "last_login")


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"


class ProductSerializer(serializers.ModelSerializer):
    author = UserProductSerializer(read_only=True)

    class Meta:
        model = Product
        fields = "__all__"


class ProductListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        exclude = ("author", "description", "phone_number")


class ProductImageSerializer(serializers.ModelSerializer):
    """Serializer for uploading images to products."""

    class Meta:
        model = Product
        fields = ["id", "image"]
        read_only_fields = ["id"]
        extra_kwargs = {"image": {"required": "True"}}
