from rest_framework import serializers

from .models import Cart, CartItem
from products.serializers import ProductSerializer
from django.db.models import F, Sum

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
            "session_key",
            "user",
            "items",
            "total_price",
            "total_items",
            "created_at",
        ]

    def get_total_price(self, obj):
        return obj.items.aggregate(
            total=Sum(F("quantity") * F("product__price"))
        )["total"] or 0

    def get_total_items(self, obj):
        return obj.items.aggregate(
            total=Sum("quantity")
        )["total"] or 0