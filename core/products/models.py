#django
from django.db import models

#packages
from django_resized import ResizedImageField
from ckeditor_uploader.fields import RichTextUploadingField


class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="نام دسته‌بندی")
    parent = models.ForeignKey('self',
                               null=True,
                               blank=True,
                               related_name='children',
                               on_delete=models.CASCADE,
                               verbose_name="والد"
                               )
    image = ResizedImageField(
        size=[800, 800],
        quality=85,
        upload_to='categories/',
        force_format='WEBP',
        blank=True, null=True,
        crop=['middle', 'center'],
        verbose_name="تصویر دسته‌بندی"
    )
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "دسته‌بندی"
        verbose_name_plural = "دسته‌بندی‌ها"

class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products', verbose_name="دسته‌بندی")
    name = models.CharField(max_length=255, db_index=True, verbose_name="نام محصول")
    description = models.TextField(verbose_name="توضیحات کوتاه")
    first_price = models.DecimalField(max_digits=12, decimal_places=0, verbose_name="قیمت اصلی")
    price = models.DecimalField(max_digits=12, decimal_places=0, verbose_name="قیمت فروش")
    stock = models.PositiveIntegerField(default=0, verbose_name="موجودی انبار")

    image = ResizedImageField(
        size=[800, 800],
        quality=85,
        upload_to='products/main/',
        force_format='WEBP',
        blank=True, null=True,
        crop=['middle', 'center'],
        verbose_name="تصویر اصلی"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    content = RichTextUploadingField(config_name='default', verbose_name="محتوای کامل محصول")

    def __str__(self):
        return f"{self.name} - موجودی: {self.stock}"

    class Meta:
        verbose_name = "محصول"
        verbose_name_plural = "محصولات"
        ordering = ['-id']


class ProductImages(models.Model):
    caption = models.CharField(max_length=300, blank=True, null=True, verbose_name="توضیح تصویر")

    image = ResizedImageField(
        size=[1200, 800],  # سایز بزرگتر برای گالری
        quality=85,
        upload_to='products/',  # مسیر اصلاح شد
        force_format='WEBP',
        blank=True, null=True,
        verbose_name="تصویر"
    )

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images', verbose_name="محصول")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.caption or f"تصویر #{self.id} - {self.product.name}"

    class Meta:
        verbose_name = "تصویر گالری"
        verbose_name_plural = "تصاویر گالری محصولات"