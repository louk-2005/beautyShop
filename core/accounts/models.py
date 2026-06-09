#django
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator

#packages
from .managers import UserManager


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

