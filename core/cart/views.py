from django.db.models import Sum
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Cart, CartItem
from .serializers import CartSerializer


class CartViewSet(viewsets.ModelViewSet):
    serializer_class = CartSerializer
    queryset = Cart.objects.all()

    def get_cart(self):
        request = self.request

        # کاربر لاگین شده
        if request.user.is_authenticated:
            print(request.user.is_authenticated)
            cart, _ = Cart.objects.get_or_create(
                user=request.user
            )
            return cart

        # کاربر مهمان
        cart_token = (
            request.data.get("cart_token")
            or request.query_params.get("cart_token")
        )

        if not cart_token:
            return None

        cart, _ = Cart.objects.get_or_create(
            cart_token=cart_token
        )

        return cart

    @action(detail=False, methods=["get"])
    def current(self, request):
        cart = self.get_cart()

        if not cart:
            return Response(
                {"detail": "cart_token is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            CartSerializer(cart).data
        )

    @action(detail=False, methods=["post"])
    def add_item(self, request):
        cart = self.get_cart()

        if not cart:
            return Response(
                {"detail": "cart_token is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        product_id = request.data.get("product_id")
        quantity = int(request.data.get("quantity", 1))

        if not product_id:
            return Response(
                {"detail": "product_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        item, created = CartItem.objects.get_or_create(
            cart=cart,
            product_id=product_id,
            defaults={
                "quantity": quantity
            }
        )

        if not created:
            item.quantity += quantity
            item.save(update_fields=["quantity"])

        return Response(
            CartSerializer(cart).data,
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=["post"])
    def remove_item(self, request):
        cart = self.get_cart()

        if not cart:
            return Response(
                {"detail": "cart_token is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        product_id = request.data.get("product_id")

        CartItem.objects.filter(
            cart=cart,
            product_id=product_id
        ).delete()

        return Response(
            CartSerializer(cart).data,
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=["get"])
    def count(self, request):
        cart = self.get_cart()

        if not cart:
            return Response({"count": 0})

        count = cart.items.aggregate(
            total=Sum("quantity")
        )["total"] or 0

        return Response({"count": count})