from django.urls import path

from .views import (
    SendOTPView,
    VerifyOTPView,
    ProfileView,
    ContactViewSet,
    SocialLinkViewSet
)
# django files
from django.urls import path, include

# rest files
from rest_framework.routers import DefaultRouter

# your files


app_name = 'accounts'
router = DefaultRouter()
router.register(r'contacts', ContactViewSet, basename='contact')
router.register(r'social/links', SocialLinkViewSet, basename='social-link')
urlpatterns = [
    path('', include(router.urls)),

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
