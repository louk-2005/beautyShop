from rest_framework import serializers

from .models import (
    Category,
    Product,
    ProductImages,
    ProductMessage
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




class ProductMessageSerializer(serializers.ModelSerializer):
    replies = serializers.SerializerMethodField()

    class Meta:
        model = ProductMessage
        fields = '__all__'

    def get_replies(self, obj):
        descendants = obj.get_descendants().filter(is_shown=True).order_by('created_at')
        return ProductMessageSerializer(descendants, many=True, context=self.context).data