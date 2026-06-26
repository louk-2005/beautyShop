from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from datetime import timedelta
from .models import User, OTP, ContactInfo, SocialLink
from django.utils.html import format_html
from django.forms import TextInput

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






class SocialLinkInline(admin.TabularInline):
    model = SocialLink
    extra = 1
    fields = ('name', 'url')
    classes = ['collapse']

    def formfield_for_dbfield(self, db_field, **kwargs):
        # Customize form fields for better UI
        if db_field.name == 'name':
            kwargs['widget'] = TextInput(attrs={'class': 'vTextField', 'style': 'width: 200px;'})
        elif db_field.name == 'url':
            kwargs['widget'] = TextInput(attrs={'class': 'vTextField', 'style': 'width: 400px;'})
        return super().formfield_for_dbfield(db_field, **kwargs)


class SocialLinkInline(admin.TabularInline):
    model = SocialLink
    extra = 1
    fields = ('name', 'url')
    classes = ['collapse']

    def formfield_for_dbfield(self, db_field, **kwargs):
        # Customize form fields for better UI
        if db_field.name == 'name':
            kwargs['widget'] = TextInput(attrs={'class': 'vTextField', 'style': 'width: 200px;'})
        elif db_field.name == 'url':
            kwargs['widget'] = TextInput(attrs={'class': 'vTextField', 'style': 'width: 400px;'})
        return super().formfield_for_dbfield(db_field, **kwargs)


@admin.register(ContactInfo)
class ContactInfoAdmin(admin.ModelAdmin):
    list_display = (
        'get_name_display', 'phone_display', 'email_display', 'address_preview', 'logo_thumbnail', 'updated_at')
    list_filter = ('name', 'updated_at')
    search_fields = ('name', 'phone', 'email', 'address', 'description')
    readonly_fields = ('logo_thumbnail', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('name', 'logo', 'logo_thumbnail')
        }),
        ('Contact Information', {
            'fields': ('phone', 'email', 'address'),
            'classes': ('collapse', 'open')
        }),
        ('Additional Information', {
            'fields': ('description',),
            'classes': ('collapse',)
        }),
        ('System Information', {
            'fields': ('updated_at',),
            'classes': ('collapse',),
            'description': 'System managed information'
        }),
    )
    inlines = [SocialLinkInline]

    def get_name_display(self, obj):
        return obj.get_name_display()

    get_name_display.short_description = 'نام شعبه'
    get_name_display.admin_order_field = 'name'

    def phone_display(self, obj):
        return obj.phone if obj.phone else '---'

    phone_display.short_description = 'تلفن'
    phone_display.admin_order_field = 'phone'

    def email_display(self, obj):
        return obj.email if obj.email else '---'

    email_display.short_description = 'ایمیل'
    email_display.admin_order_field = 'email'

    def address_preview(self, obj):
        if obj.address:
            return format_html(
                '<span title="{}">{}</span>',
                obj.address,
                (obj.address[:50] + '...') if len(obj.address) > 50 else obj.address
            )
        return '---'

    address_preview.short_description = 'آدرس'
    address_preview.admin_order_field = 'address'

    def logo_thumbnail(self, obj):
        if obj.logo:
            return format_html(
                '<img src="{}" width="100" height="100" style="object-fit: cover; border-radius: 5px;" />',
                obj.logo.url
            )
        return '---'

    logo_thumbnail.short_description = 'لوگو'
    logo_thumbnail.allow_tags = True

    def get_queryset(self, request):
        # FIXED: Use prefetch_related for reverse relationships
        return super().get_queryset(request).prefetch_related('social_links')

    class Media:
        css = {
            'all': ('admin/css/custom_admin.css',)
        }
        js = ('admin/js/custom_admin.js',)


@admin.register(SocialLink)
class SocialLinkAdmin(admin.ModelAdmin):
    list_display = ('name', 'url_display', 'contact_name', 'get_contact_name_display')
    list_filter = ('contact__name', 'name')
    search_fields = ('name', 'url', 'contact__name')
    # CORRECT: Use select_related for forward relationships
    list_select_related = ('contact',)

    def url_display(self, obj):
        return format_html(
            '<a href="{}" target="_blank">{}</a>',
            obj.url,
            (obj.url[:30] + '...') if len(obj.url) > 30 else obj.url
        )

    url_display.short_description = 'لینک'
    url_display.allow_tags = True

    def contact_name(self, obj):
        return obj.contact.name

    contact_name.short_description = 'شعبه'
    contact_name.admin_order_field = 'contact__name'

    def get_contact_name_display(self, obj):
        return obj.contact.get_name_display()

    get_contact_name_display.short_description = 'نام شعبه'
    get_contact_name_display.admin_order_field = 'contact__name'

    fieldsets = (
        (None, {
            'fields': ('contact', 'name', 'url')
        }),
    )

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "contact":
            kwargs["queryset"] = ContactInfo.objects.all()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    class Media:
        css = {
            'all': ('admin/css/custom_admin.css',)
        }
