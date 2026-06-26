from rest_framework import serializers
from django.db.models import F, Sum

from .models import Cart, CartItem
from products.serializers import ProductSerializer


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    item_total = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = [
            "id",
            "product",
            "quantity",
            "item_total",
            "created_at",
        ]

    def get_item_total(self, obj):
        if obj.product and obj.product.price:
            return obj.product.price * obj.quantity
        return 0


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)

    total_price = serializers.SerializerMethodField()
    total_items = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = [
            "id",
            "cart_token",
            "user",
            "items",
            "total_price",
            "total_items",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "cart_token",
            "total_price",
            "total_items",
            "created_at",
            "updated_at",
        ]

    def get_total_price(self, obj):
        result = obj.items.aggregate(
            total=Sum(F("quantity") * F("product__price"))
        )

        return result["total"] or 0

    def get_total_items(self, obj):
        result = obj.items.aggregate(
            total=Sum("quantity")
        )

        return result["total"] or 0