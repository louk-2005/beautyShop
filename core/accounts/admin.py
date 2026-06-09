from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from datetime import timedelta
from .models import User, OTP


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    # نمایش فیلدها در لیست کاربران
    list_display = ('phone_number', 'email', 'first_name', 'last_name', 'is_staff', 'is_active', 'date_joined')

    # فیلترهای سمت راست (در Jazzmin بسیار زیبا نمایش داده می‌شود)
    list_filter = ('is_staff', 'is_active', 'groups')

    # جستجو
    search_fields = ('phone_number', 'first_name', 'last_name', 'email')

    ordering = ('-date_joined',)

    # قابلیت ویرایش مستقیم در لیست
    list_editable = ('is_active',)

    # نمایش دکمه‌های ذخیره در بالای صفحه نیز (سهولت دسترسی)
    save_on_top = True

    # تنظیم فیلدها برای صفحه ویرایش
    # در Jazzmin می‌توانیم از کلاس‌های خاص برای جمع‌شدن (collapse) استفاده کنیم
    fieldsets = (
        (None, {'fields': ('phone_number', 'password')}),
        (_('اطلاعات شخصی'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('دسترسی‌ها'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
            'classes': ('collapse',),  # این بخش در حالت پیش‌فرض جمع می‌شود
        }),
        (_('تاریخ‌های مهم'), {'fields': ('last_login', 'date_joined')}),
    )

    # تنظیم فیلدها برای صفحه ساخت کاربر جدید
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone_number', 'password1', 'password2'),
        }),
    )

    # فعال کردن قابلیت ذخیره و ادامه ویرایش در پنجره جدید (مخصوص Jazzmin)
    save_as = True
    save_as_continue = True


@admin.register(OTP)
class OTPAdmin(admin.ModelAdmin):
    list_display = ('phone_number', 'code', 'created_at', 'is_verified', 'is_expired')
    list_filter = ('is_verified', 'created_at')
    search_fields = ('phone_number', 'code')
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)

    # قابلیت ناوبری تاریخ (بسیار کاربردی در Jazzmin)
    date_hierarchy = 'created_at'

    # نمایش تمام رکوردها در یک صفحه؟ خیر، paginate بهتر است
    list_per_page = 20

    actions = ['mark_as_verified', 'delete_expired_otps']

    @admin.action(description='تایید کردن کدهای انتخاب شده')
    def mark_as_verified(self, request, queryset):
        updated = queryset.update(is_verified=True)
        self.message_user(request, f'{updated} کد با موفقیت تایید شد.')

    @admin.action(description='حذف کدهای منقضی شده (بیش از ۲ دقیقه)')
    def delete_expired_otps(self, request, queryset):
        expiration_time = timezone.now() - timedelta(minutes=2)
        # برای عملکرد بهتر، فیلتر را روی کل کوئری اعمال می‌کنیم نه فقط انتخاب شده‌ها
        # اما طبق استاندارد اکشن، روی queryset ورودی کار می‌کنیم
        expired_otps = queryset.filter(created_at__lt=expiration_time)
        count = expired_otps.count()
        expired_otps.delete()
        self.message_user(request, f'{count} کد منقضی شده حذف گردید.')

    @admin.display(boolean=True, description='منقضی شده؟')
    def is_expired(self, obj):
        return obj.created_at < timezone.now() - timedelta(seconds=120)