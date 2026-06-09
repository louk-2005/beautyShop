from django.db import models
from django.core.validators import MinLengthValidator, RegexValidator

# models
from accounts.models import User
from cart.models import Cart
from products.models import Product


class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "در انتظار پرداخت"
        PAID = "paid", "پرداخت شده"
        SHIPPED = "shipped", "در حال ارسال"
        DELIVERED = "delivered", "تحویل داده شده"
        CANCELED = "canceled", "لغو شده"

    user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,  
        related_name="orders",
        verbose_name="کاربر"
    )

    full_name = models.CharField(max_length=255, verbose_name="نام و نام خانوادگی")

    phone_number = models.CharField(
        max_length=11,
        validators=[
            MinLengthValidator(11),
            RegexValidator(r'^09\d{9}$', message="شماره تلفن باید معتبر باشد (شروع با 09)")
        ],
        verbose_name="شماره تماس"
    )

    province = models.CharField(max_length=100, verbose_name="استان")
    city = models.CharField(max_length=100, verbose_name="شهر")
    postal_code = models.CharField(
        max_length=10,
        verbose_name="کد پستی"
    )
    address = models.TextField(verbose_name="آدرس کامل")

    total_price = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        default=0,
        verbose_name="مبلغ کل سفارش"
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name="وضعیت سفارش"
    )
    payment_authority = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    payment_ref_id = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    paid_at = models.DateTimeField(
        blank=True,
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ثبت")

    def __str__(self):
        return f"سفارش #{self.id} - {self.full_name}"

    class Meta:
        verbose_name = 'سفارش'
        verbose_name_plural = 'سفارش‌ها'
        ordering = ['-created_at']


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="سفارش"
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        verbose_name="محصول"
    )

    quantity = models.PositiveIntegerField(verbose_name="تعداد")

    price = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        default=0,
        verbose_name="قیمت واحد (در لحظه خرید)"
    )

    @property
    def total_item_price(self):
        """محاسبه قیمت کل برای این آیتم (تعداد × قیمت واحد)"""
        return self.quantity * self.price

    def __str__(self):
        return f"{self.product.name} ({self.quantity} عدد)"

    class Meta:
        verbose_name = "آیتم سفارش"
        verbose_name_plural = "آیتم‌های سفارش"