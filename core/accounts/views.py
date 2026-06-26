#another files
from secrets import randbelow

#django
from django.contrib.auth import get_user_model

#rest api
from rest_framework import status
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated
)
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import viewsets

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.decorators import action as Action

#models
from .models import OTP,SocialLink,ContactInfo
from .serializers import (
    SendOTPSerializer,
    VerifyOTPSerializer,
    UserSerializer,
    SocialLinkSerializer,
    ContactInfoSerializer
)
from cart.models import Cart
from .sms import send_otp

User = get_user_model()


class SendOTPView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "send_otp"
    def post(self, request):
        serializer = SendOTPSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        phone_number = serializer.validated_data[
            "phone_number"
        ]

        # حذف OTP های قبلی
        OTP.objects.filter(
            phone_number=phone_number,
            is_verified=False
        ).delete()

        code = str(
            randbelow(900000) + 100000
        )

        OTP.objects.create(
            phone_number=phone_number,
            code=code
        )

        # اینجا سرویس پیامک را صدا بزن
        success = send_otp(
            phone_number=phone_number,
            code=code
        )

        if not success:
            return Response(
                {
                    "message": "خطا در ارسال پیامک"
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        return Response(
            {
                "message":
                    "کد تایید ارسال شد."
            },
            status=status.HTTP_200_OK
        )


class VerifyOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = VerifyOTPSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        otp = serializer.validated_data["otp"]

        otp.is_verified = True
        otp.save(update_fields=["is_verified"])

        user, created = User.objects.get_or_create(
            phone_number=otp.phone_number,
            defaults={"is_active": True}
        )

        # ------------------------------
        # Merge Guest Cart
        # ------------------------------

        cart_token = request.data.get(
            "cart_token"
        )

        if cart_token:

            guest_cart = Cart.objects.filter(
                cart_token=cart_token,
                user__isnull=True
            ).first()

            if guest_cart:

                user_cart, _ = Cart.objects.get_or_create(
                    user=user
                )

                for guest_item in guest_cart.items.all():

                    user_item = user_cart.items.filter(
                        product=guest_item.product
                    ).first()

                    if user_item:
                        user_item.quantity += (
                            guest_item.quantity
                        )

                        user_item.save(
                            update_fields=["quantity"]
                        )

                    else:
                        guest_item.cart = user_cart
                        guest_item.save(
                            update_fields=["cart"]
                        )

                guest_cart.delete()

        # ------------------------------

        refresh = RefreshToken.for_user(
            user
        )

        return Response(
            {
                "message":
                    "ورود موفقیت آمیز بود.",

                "access":
                    str(refresh.access_token),

                "refresh":
                    str(refresh),

                "is_new_user":
                    created
            },
            status=status.HTTP_200_OK
        )

class ProfileView(APIView):
    permission_classes = [
        IsAuthenticated
    ]

    def get(self, request):
        serializer = UserSerializer(
            request.user
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    def patch(self, request):
        serializer = UserSerializer(
            request.user,
            data=request.data,
            partial=True
        )

        serializer.is_valid(
            raise_exception=True
        )

        serializer.save()

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )




class ContactViewSet(viewsets.ModelViewSet):
    queryset = ContactInfo.objects.all()
    serializer_class = ContactInfoSerializer

    @Action(detail=True, methods=['get'])
    def get_social_links(self, request, pk=None):
        contact = self.get_object()
        social_links = SocialLink.objects.filter(contact=contact)
        serializer = SocialLinkSerializer(social_links, many=True)
        return Response(serializer.data)


class SocialLinkViewSet(viewsets.ModelViewSet):
    queryset = SocialLink.objects.all()
    serializer_class = SocialLinkSerializer