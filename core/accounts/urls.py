from django.urls import path

from .views import (
    SendOTPView,
    VerifyOTPView,
    ProfileView
)

app_name = 'accounts'

urlpatterns = [
    path(
        "send-otp/",
        SendOTPView.as_view(),
        name="send-otp"
    ),

    path(
        "verify-otp/",
        VerifyOTPView.as_view(),
        name="verify-otp"
    ),

    path(
        "profile/",
        ProfileView.as_view(),
        name="profile"
    ),
]
