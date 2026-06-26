#django
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator

#packages
from .managers import UserManager
from PIL import Image


class User(AbstractUser):
    username = None

    phone_regex = RegexValidator(
        regex=r'^\d{11}$',
        message="Phone number must be exactly 11 digits."
    )
    phone_number = models.CharField(max_length=11, unique=True, validators=[phone_regex])

    USERNAME_FIELD = "phone_number"
    REQUIRED_FIELDS = []
    objects = UserManager()

    def __str__(self):
        return self.phone_number
    class Meta:
        verbose_name = 'کاربر'
        verbose_name_plural = 'کاربران'

class OTP(models.Model):
    phone_number = models.CharField(
        max_length=11
    )

    code = models.CharField(
        max_length=6
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    is_verified = models.BooleanField(
        default=False
    )
    class Meta:
        ordering = ["-created_at"]

# class Address(models.Model):
#     user = models.ForeignKey(
#         User,
#         on_delete=models.CASCADE,
#         related_name='addresses',
#         null=True,
#         blank=True,
#         verbose_name='کاربر'
#     )
#     full_name = models.CharField(
#         max_length=255,
#         verbose_name='نام کامل'
#     )
#
#     province = models.CharField(
#         max_length=100,
#         verbose_name='استان'
#     )
#
#     city = models.CharField(
#         max_length=100,
#         verbose_name='شهر'
#     )
#     address = models.TextField(verbose_name='ادرس')
#     postal_code = models.CharField(
#         max_length=20,
#         verbose_name='کد پستی'
#     )





class ContactInfo(models.Model):
    NAME_CHOICES = [
        ('Head Office', 'شعبه اصلی'),
        ('Other Branches', 'سایر شعبه ها'),
    ]
    name = models.CharField(choices=NAME_CHOICES, max_length=55, default='FACTORY')
    logo = models.ImageField(upload_to='logos/', blank=True, null=True)
    description = models.TextField(verbose_name="communicate with us", blank=True)
    phone = models.CharField(max_length=11, blank=True, null=True)
    email = models.EmailField(blank=True)
    address = models.CharField(max_length=255, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.pk:
            orig = ContactInfo.objects.filter(pk=self.pk).first()
            orig_image = orig.logo if orig else None
        else:
            orig_image = None

        super().save(*args, **kwargs)

        if self.logo and self.logo != orig_image:
            image_path = self.logo.path
            with Image.open(image_path) as img:
                max_size = (300, 300)
                img.thumbnail(max_size)
                img.save(image_path, quality=85)

    def __str__(self):
        return f"{self.name}-Contact information"


class SocialLink(models.Model):
    contact = models.ForeignKey(ContactInfo, related_name='social_links', on_delete=models.CASCADE)
    name = models.CharField(max_length=50, verbose_name="field name")
    url = models.URLField(verbose_name="link url")

    def __str__(self):
        return f"{self.name} - {self.url}"

