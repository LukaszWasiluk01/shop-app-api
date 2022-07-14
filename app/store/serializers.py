from rest_framework import serializers
from core.models import Product, Category
from django.contrib.auth import get_user_model

UserModel = get_user_model()


class UserProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = ('id', 'username', 'date_joined', 'last_login')


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"


class ProductSerializer(serializers.ModelSerializer):
    author = UserProductSerializer(read_only=True)

    class Meta:
        model = Product
        fields = '__all__'


class ProductListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        exclude = ('author', 'description', 'phone_number')
