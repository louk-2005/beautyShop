from datetime import timedelta

from django.utils import timezone
from rest_framework import serializers

from .models import User, OTP


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
        read_only_fields = ("id",)


class SendOTPSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=11)

    def validate_phone_number(self, value):
        if len(value) != 11:
            raise serializers.ValidationError(
                "شماره تلفن باید 11 رقم باشد."
            )

        if not value.isdigit():
            raise serializers.ValidationError(
                "شماره تلفن نامعتبر است."
            )

        return value


class VerifyOTPSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=11)
    code = serializers.CharField(max_length=6)

    def validate(self, attrs):
        phone_number = attrs.get("phone_number")
        code = attrs.get("code")

        otp = OTP.objects.filter(
            phone_number=phone_number,
            code=code,
            is_verified=False
        ).first()

        if not otp:
            raise serializers.ValidationError(
                "کد تایید نامعتبر است."
            )

        # اعتبار 2 دقیقه
        if timezone.now() - otp.created_at > timedelta(minutes=2):
            raise serializers.ValidationError(
                "کد تایید منقضی شده است."
            )

        attrs["otp"] = otp

        return attrs