from django.db import models
from django.conf import settings  # برای استفاده از مدل User
from products.models import Product
import uuid


class Cart(models.Model):
    session_key = models.CharField(
        max_length=40,
        null=True,
        blank=True,
        db_index=True,
        unique=True,
        verbose_name="کلید سشن"
    )
    # اتصال به کاربر (اختیاری - برای کاربران لاگین شده)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='carts',
        verbose_name="کاربر"
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")

    def __str__(self):
        # نمایش بهتر: اگر کاربر دارد نام کاربر، وگرنه آیدی سبد
        if self.user:
            return f"سبد خرید {self.user.phone_number}"
        return f"سبد خرید مهمان ({str(self.id)[:8]})"

    class Meta:
        verbose_name = "سبد خرید"
        verbose_name_plural = "سبدهای خرید"


class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="دسته بندی"
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name="محصول"
    )
    quantity = models.PositiveIntegerField(default=1, verbose_name="تعداد")
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"{self.quantity} عدد {self.product.name}"

    class Meta:
        unique_together = ("cart", "product")
        verbose_name = "آیتم سبد خرید"
        verbose_name_plural = "آیتم‌های سبد خرید"