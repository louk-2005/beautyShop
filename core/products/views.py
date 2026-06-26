from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from rest_framework.decorators import action as Action

# from django_filters.rest_framework import DjangoFilterBackend

from .models import Product, Category,ProductMessage
from .serializers import ProductSerializer, CategorySerializer,ProductMessageSerializer
from .paginations import CustomPagination

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
    @Action(detail=True, methods=['get'])
    def get_product_message(self, request, pk=None):
        product = self.get_object()
        messages = ProductMessage.objects.filter(product=product, is_shown=True).order_by('-created_at')

        paginator = CustomPagination()
        page = paginator.paginate_queryset(messages, request)
        serializer = ProductMessageSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

class MessageViewSet(viewsets.ModelViewSet):
    queryset = ProductMessage.objects.all()
    serializer_class = ProductMessageSerializer
    pagination_class = CustomPagination

