# django files
from django.db import models
from django.core.validators import RegexValidator

# package files
from PIL import Image

class Location(models.Model):
    name = models.CharField(max_length=50, verbose_name='نام')
    image = models.ImageField(upload_to='location/images', blank=True, null=True, verbose_name='تصویر')
    description = models.TextField( blank=True, null=True, verbose_name='توضیحات')
    latitude = models.DecimalField(max_digits=9, decimal_places=6, verbose_name="Latitude")
    longitude = models.DecimalField(max_digits=9, decimal_places=6, verbose_name="Longitude")

    class Meta:
        verbose_name = "موقعیت مکانی"
        verbose_name_plural = "موقعیت مکانی"
        ordering = ['name']

    def save(self, *args, **kwargs):
        if self.pk:
            orig = Location.objects.filter(pk=self.pk).first()
            orig_image = orig.image if orig else None
        else:
            orig_image = None

        super().save(*args, **kwargs)

        if self.image and (not orig_image or self.image.name != orig_image.name):
            self.resize_image()

    def resize_image(self):
        image_path = self.image.path
        try:
            with Image.open(image_path) as img:
                target_size = (220, 120)
                resized_img = img.resize(target_size, Image.LANCZOS)
                format = img.format or 'JPEG'
                resized_img.save(image_path, format=format, quality=95)
        except Exception as e:
            print(f"Error resizing image: {e}")

    def __str__(self):
        return self.name

class CommunicationWithUs(models.Model):
    phone_regex = RegexValidator(
        regex=r'^\d{11}$',
        message="Phone number must be exactly 11 digits."
    )
    full_name = models.CharField(max_length=50,verbose_name='نام کامل')
    email = models.EmailField(verbose_name='ایمیل')
    phone = models.CharField(max_length=11, validators=[phone_regex], blank=True, null=True,verbose_name='شماره تماس')
    message = models.TextField(blank=True, verbose_name='متن پیام')
    created_at = models.DateTimeField(auto_now_add=True,verbose_name='تاریخ ایجاد')
    is_read = models.BooleanField(default=False,verbose_name='خوانده شده')
    class Meta:
        verbose_name = "ارتباط با ما"
        verbose_name_plural = "ارتباط با ما"
        ordering = ['phone']
    def __str__(self):
        return f"{self.full_name} - {self.email} - {self.phone} - {self.message[:20]}"