# django files
from django.db import models
from django_resized import ResizedImageField
# your packages


class HomeImage(models.Model):
    name = models.CharField(max_length=100, unique=True,verbose_name="نام")
    description = models.TextField(blank=True,verbose_name="توضیحات")
    image = ResizedImageField(
        size=[2000, 1500],  # سایز خروجی (عرض × ارتفاع)
        quality=75,  # کیفیت (0 تا 100)
        upload_to='article_images/',  # مسیر ذخیره‌سازی
        force_format='WEBP',  # تبدیل فرمت (jpg, png, webp و غیره)
        blank=True, null=True,
        verbose_name="تصویر اصلی"
    )
    show = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True,verbose_name="تاریخ ایجاد")

    class Meta:
        verbose_name = "تصاویر صفحه خانه"
        verbose_name_plural = "تصاویر صفحه خانه"
        ordering = ['created_at']

    def __str__(self):
        return self.name

