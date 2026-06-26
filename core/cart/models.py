from django.db import models
from django.conf import settings
from products.models import Product
import uuid


class Cart(models.Model):
    # برای کاربران مهمان
    cart_token = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
        db_index=True,
        verbose_name="توکن سبد خرید"
    )

    # برای کاربران لاگین شده
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="carts",
        verbose_name="کاربر"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ ایجاد"
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="آخرین بروزرسانی"
    )

    def __str__(self):
        if self.user:
            return f"سبد خرید {self.user.phone_number}"

        return f"Guest Cart ({self.cart_token})"

    class Meta:
        verbose_name = "سبد خرید"
        verbose_name_plural = "سبدهای خرید"


class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="سبد خرید"
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name="محصول"
    )

    quantity = models.PositiveIntegerField(
        default=1,
        verbose_name="تعداد"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.quantity} × {self.product.name}"

    class Meta:
        unique_together = ("cart", "product")
        verbose_name = "آیتم سبد خرید"
        verbose_name_plural = "آیتم‌های سبد خرید"