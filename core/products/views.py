from rest_framework import viewsets
from rest_framework.permissions import AllowAny
# from django_filters.rest_framework import DjangoFilterBackend

from .models import Product, Category
from .serializers import ProductSerializer, CategorySerializer


class CategoryViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows categories to be viewed or edited.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]  # یا IsAuthenticated اگر نیاز به لاگین دارید
    # filter_backends = [DjangoFilterBackend]
    # filterset_fields = ['name', 'parent']


class ProductViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows products to be viewed or edited.
    """



    serializer_class = ProductSerializer
    permission_classes = [AllowAny]

    # # اضافه کردن قابلیت فیلتر و جستجو
    # filter_backends = [DjangoFilterBackend]
    # filterset_fields = ['category', 'name', 'stock']

    def get_queryset(self):
        """
        بهینه‌سازی کوئری‌ها برای جلوگیری از درخواست‌های متعدد به دیتابیس.
        select_related: برای رابطه یک به چند (ForeignKey) مانند category
        prefetch_related: برای رابطه چند به چند یا معکوس یک به چند مانند images
        """
        return Product.objects.select_related('category').prefetch_related('images').all()