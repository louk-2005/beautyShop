from rest_framework import serializers

from .models import (
    Category,
    Product,
    ProductImages
)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class ProductImagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImages
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    images = ProductImagesSerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True)

    class Meta:
        model = Product
        fields = [
            "id",
            "category",
            "name",
            "description",
            "first_price",
            "price",
            "stock",
            "image",
            "content",
            "images",
            "created_at",
        ]