"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

#django
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

#rest
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('ckeditor/', include('ckeditor_uploader.urls')),
    path('api/v1/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/v1/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/v1/accounts/', include('accounts.urls', namespace='accounts')),
    path('api/v1/products/', include('products.urls', namespace='products')),
    path('api/v1/cart/', include('cart.urls', namespace='cart')),
    path('api/v1/orders/', include('orders.urls', namespace='orders')),
    path('api/v1/contactUs', include('contactUs.urls', namespace='contactUs')),
    path('api/v1/site/assets/', include('siteAssets.urls', namespace='assets')),

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
