from rest_framework import serializers

from .models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(
        source="product.name",
        read_only=True
    )

    total_item_price = serializers.ReadOnlyField()

    class Meta:
        model = OrderItem
        fields = [
            "id",
            "product",
            "product_name",
            "quantity",
            "price",
            "total_item_price",
        ]
        read_only_fields = [
            "price",
        ]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(
        many=True,
        read_only=True
    )

    class Meta:
        model = Order
        fields = [
            "id",
            "user",
            "full_name",
            "phone_number",
            "province",
            "city",
            "postal_code",
            "address",
            "total_price",
            "status",
            "payment_authority",
            "payment_ref_id",
            "paid_at",
            "created_at",
            "items",
        ]
        read_only_fields = [
            "id",
            "user",
            "total_price",
            "status",
            "payment_authority",
            "payment_ref_id",
            "paid_at",
            "created_at",
        ]


class CreateOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = [
            "full_name",
            "phone_number",
            "province",
            "city",
            "postal_code",
            "address",
        ]

    def validate_postal_code(self, value):
        if not value.isdigit() or len(value) != 10:
            raise serializers.ValidationError(
                "کد پستی باید 10 رقم باشد."
            )
        return value