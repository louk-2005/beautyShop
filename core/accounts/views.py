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

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.throttling import ScopedRateThrottle

#models
from .models import OTP
from .serializers import (
    SendOTPSerializer,
    VerifyOTPSerializer,
    UserSerializer
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
        serializer = VerifyOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        otp = serializer.validated_data['otp']

        otp.is_verified = True
        otp.save(update_fields=["is_verified"])

        user, created = User.objects.get_or_create(
            phone_number=otp.phone_number,
            defaults={"is_active": True}
        )

        # --- بخش جدید: انتقال سبد خرید مهمان به کاربر ---
        session_key = request.session.session_key
        if session_key:
            try:
                # سبد خریدی که کاربر مهمان ساخته但没有 یوزر دارد
                guest_cart = Cart.objects.get(session_key=session_key, user__isnull=True)
                # اگر کاربر قبلا سبد خرید داشت، می‌توانید ادغام کنید یا جایگزین کنید
                # اینجا سبد مهمان را به یوزر اختصاص می‌دهیم
                guest_cart.user = user
                guest_cart.session_key = None  # سشن را پاک می‌کنیم
                guest_cart.save()
            except Cart.DoesNotExist:
                pass
        # ---------------------------------------------

        refresh = RefreshToken.for_user(user)

        return Response({
            "message": "ورود موفقیت آمیز بود.",
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "is_new_user": created
        }, status=status.HTTP_200_OK)


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