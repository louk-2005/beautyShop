from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, CategoryViewSet,MessageViewSet



app_name = 'products'

router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='products')
router.register(r'categories', CategoryViewSet, basename='categories')
router.register(r'message', MessageViewSet, basename='message')

urlpatterns = [
    path('', include(router.urls)),
]