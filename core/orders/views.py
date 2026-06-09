from django.db import transaction
from django.shortcuts import get_object_or_404

from rest_framework import status, generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


from cart.models import Cart, CartItem
from .models import Order, OrderItem
from .serializers import (
    CreateOrderSerializer,
    OrderSerializer
)


from django.conf import settings
import requests
from django.utils import timezone


class CreateOrderView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        serializer = CreateOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        cart = get_object_or_404(
            Cart.objects.prefetch_related(
                "items__product"
            ),
            user=request.user
        )

        cart_items = cart.items.all()

        if not cart_items.exists():
            return Response(
                {
                    "detail": "سبد خرید خالی است."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        total_price = 0

        order = Order.objects.create(
            user=request.user,
            full_name=serializer.validated_data["full_name"],
            phone_number=serializer.validated_data["phone_number"],
            province=serializer.validated_data["province"],
            city=serializer.validated_data["city"],
            postal_code=serializer.validated_data["postal_code"],
            address=serializer.validated_data["address"],
        )

        order_items = []

        for item in cart_items:
            product_price = item.product.price

            order_items.append(
                OrderItem(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    price=product_price,
                )
            )

            total_price += product_price * item.quantity

        OrderItem.objects.bulk_create(order_items)

        order.total_price = total_price
        order.save(update_fields=["total_price"])

        # پاک کردن سبد خرید
        # cart_items.delete()

        return Response(
            OrderSerializer(order).data,
            status=status.HTTP_201_CREATED
        )


class OrderListView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return (
            Order.objects
            .filter(user=self.request.user)
            .prefetch_related(
                "items",
                "items__product"
            )
            .order_by("-created_at")
        )


class OrderDetailView(generics.RetrieveAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return (
            Order.objects
            .filter(user=self.request.user)
            .prefetch_related(
                "items",
                "items__product"
            )
        )




class StartPaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, order_id):

        order = get_object_or_404(
            Order,
            id=order_id,
            user=request.user
        )

        if order.status == Order.Status.PAID:
            return Response(
                {"detail": "این سفارش قبلا پرداخت شده است."},
                status=status.HTTP_400_BAD_REQUEST
            )

        callback_url = (
            f"{settings.SITE_URL}"
            f"/api/orders/verify-payment/"
        )

        payload = {
            "merchant_id": settings.ZARINPAL_MERCHANT_ID,
            "amount": int(order.total_price),
            "currency": "IRT",
            "description": f"پرداخت سفارش شماره {order.id}",
            "callback_url": callback_url,
            "metadata": {
                "mobile": order.phone_number,
                "order_id": str(order.id)
            }
        }

        headers = {
            "accept": "application/json",
            "content-type": "application/json"
        }

        response = requests.post(
            settings.ZARINPAL_REQUEST_URL,
            json=payload,
            headers=headers,
            timeout=20
        )

        result = response.json()

        if result["data"]["code"] != 100:
            return Response(
                result,
                status=status.HTTP_400_BAD_REQUEST
            )

        authority = result["data"]["authority"]

        order.payment_authority = authority
        order.save(update_fields=["payment_authority"])

        payment_url = (
            f"{settings.ZARINPAL_STARTPAY_URL}"
            f"{authority}"
        )

        return Response({
            "payment_url": payment_url,
            "authority": authority
        })



class VerifyPaymentView(APIView):

    def get(self, request):

        authority = request.GET.get("Authority")
        payment_status = request.GET.get("Status")

        if payment_status != "OK":
            return Response(
                {"detail": "پرداخت لغو شد."},
                status=status.HTTP_400_BAD_REQUEST
            )

        order = get_object_or_404(
            Order,
            payment_authority=authority
        )

        payload = {
            "merchant_id": settings.ZARINPAL_MERCHANT_ID,
            "amount": int(order.total_price),
            "authority": authority
        }

        headers = {
            "accept": "application/json",
            "content-type": "application/json"
        }

        response = requests.post(
            settings.ZARINPAL_VERIFY_URL,
            json=payload,
            headers=headers,
            timeout=20
        )

        result = response.json()

        code = result["data"]["code"]

        if code not in [100, 101]:
            return Response(
                {
                    "detail": "پرداخت ناموفق بود.",
                    "zarinpal_response": result
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        order.status = Order.Status.PAID
        order.payment_ref_id = result["data"]["ref_id"]
        order.paid_at = timezone.now()

        order.save(
            update_fields=[
                "status",
                "payment_ref_id",
                "paid_at"
            ]
        )

        CartItem.objects.filter(
            cart__user=order.user
        ).delete()

        return Response({
            "message": "پرداخت موفق",
            "ref_id": result["data"]["ref_id"],
            "order_id": order.id
        })