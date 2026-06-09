from django.utils.crypto import get_random_string
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action

from .models import Cart, CartItem
from .serializers import CartSerializer


class CartViewSet(viewsets.ModelViewSet):
    serializer_class = CartSerializer
    queryset = Cart.objects.all()

    # ----------------------------
    # گرفتن یا ساختن cart
    # ----------------------------
    def get_cart(self):
        request = self.request

        # اگر کاربر لاگین کرده
        if request.user.is_authenticated:
            cart, _ = Cart.objects.get_or_create(user=request.user)
            return cart

        # اگر کاربر مهمان است → session_key
        session_key = request.session.session_key

        if not session_key:
            request.session.create()
            session_key = request.session.session_key

        cart, _ = Cart.objects.get_or_create(session_key=session_key)
        return cart

    # ----------------------------
    # list cart (فقط cart خود کاربر)
    # ----------------------------
    def list(self, request, *args, **kwargs):
        cart = self.get_cart()
        serializer = self.get_serializer(cart)
        return Response(serializer.data)

    # ----------------------------
    # retrieve cart
    # ----------------------------
    def retrieve(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    # ----------------------------
    # add item to cart
    # ----------------------------
    @action(detail=False, methods=["post"])
    def add_item(self, request):
        cart = self.get_cart()

        product_id = request.data.get("product_id")
        quantity = int(request.data.get("quantity", 1))

        if not product_id:
            return Response(
                {"error": "product_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        item, created = CartItem.objects.get_or_create(
            cart=cart,
            product_id=product_id,
            defaults={"quantity": quantity}
        )

        if not created:
            item.quantity += quantity
            item.save()

        return Response(
            CartSerializer(cart).data,
            status=status.HTTP_200_OK
        )

    # ----------------------------
    # remove item
    # ----------------------------
    @action(detail=False, methods=["post"])
    def remove_item(self, request):
        cart = self.get_cart()

        product_id = request.data.get("product_id")

        CartItem.objects.filter(
            cart=cart,
            product_id=product_id
        ).delete()

        return Response(
            CartSerializer(cart).data,
            status=status.HTTP_200_OK
        )