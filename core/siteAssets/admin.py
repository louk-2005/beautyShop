from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from .models import HomeImage


@admin.register(HomeImage)
class HomeImageAdmin(admin.ModelAdmin):
    # تنظیمات نمایش لیست
    list_display = ('image_thumbnail', 'name', 'created_at', 'description_excerpt', 'image_info', 'show')
    list_display_links = ('image_thumbnail', 'name')
    list_filter = ('created_at',)
    search_fields = ('name', 'description')
    ordering = ('-created_at',)

    # تنظیمات فرم ویرایش
    fieldsets = (
        (None, {
            'fields': ('name', 'image', 'current_image', 'show'),
            'classes': ('wide', 'extrapretty'),
        }),
        ('توضیحات', {
            'fields': ('description',),
            'classes': ('collapse',),
        }),
        ('اطلاعات سیستمی', {
            'fields': ('created_at', 'image_info'),
            'classes': ('collapse',),
            'description': 'اطلاعات فنی و سیستمی مربوط به تصویر'
        }),
    )
    readonly_fields = ('created_at', 'image_info', 'current_image')

    # تنظیمات اضافی
    date_hierarchy = 'created_at'
    save_on_top = True
    list_per_page = 15

    # متد برای نمایش پیش‌نمایش تصویر در لیست
    @admin.display(description='پیش‌نمایش')
    def image_thumbnail(self, obj):
        if obj.image:
            return format_html(
                '<a href="{}" target="_blank">'
                '<img src="{}" width="120" height="80" style="object-fit: cover; '
                'border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.15); '
                'transition: transform 0.2s;" onmouseover="this.style.transform=\'scale(1.05)\'" '
                'onmouseout="this.style.transform=\'scale(1)\'" /></a>',
                obj.image.url,
                obj.image.url
            )
        return mark_safe('<span style="color: #999; font-style: italic;">بدون تصویر</span>')

    # متد برای نمایش تصویر فعلی در صفحه ویرایش
    @admin.display(description='تصویر فعلی')
    def current_image(self, obj):
        if obj.image:
            return format_html(
                '<div style="margin: 10px 0;">'
                '<a href="{}" target="_blank">'
                '<img src="{}" width="300" height="200" style="object-fit: cover; '
                'border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.15); '
                'border: 1px solid #ddd; padding: 5px; background: white;" /></a>'
                '<div style="margin-top: 10px; font-size: 12px; color: #666;">'
                'برای مشاهده تصویر در اندازه اصلی، روی آن کلیک کنید'
                '</div></div>',
                obj.image.url,
                obj.image.url
            )
        return mark_safe('<span style="color: #999; font-style: italic;">هیچ تصویری آپلود نشده است</span>')

    # متد برای نمایش خلاصه توضیحات
    @admin.display(description='توضیحات')
    def description_excerpt(self, obj):
        if len(obj.description) > 60:
            return f'{obj.description[:60]}...'
        return obj.description

    # متد برای نمایش اطلاعات تصویر
    @admin.display(description='اطلاعات تصویر')
    def image_info(self, obj):
        if obj.image:
            try:
                width = obj.image.width
                height = obj.image.height
                size = obj.image.size // 1024  # به کیلوبایت
                return mark_safe(
                    f'<div style="direction: ltr; text-align: left;">'
                    f'<strong>ابعاد:</strong> {width}×{height}px<br>'
                    f'<strong>حجم:</strong> {size}KB<br>'
                    f'<strong>فرمت:</strong> {obj.image.name.split(".")[-1].upper()}'
                    f'</div>'
                )
            except Exception as e:
                return mark_safe(f'<span style="color: #ff6b6b;">خطا در خواندن اطلاعات: {str(e)}</span>')
        return "اطلاعات موجود نیست"

    # تنظیمات ظاهری
    class Media:
        css = {
            'all': ('admin/css/custom_admin.css', 'admin/css/image_admin.css')
        }
        js = ('admin/js/image_admin.js',)

    # متد برای نمایش بهتر در صفحه اصلی ادمین
    def get_queryset(self, request):
        return super().get_queryset(request)

    def get_readonly_fields(self, request, obj=None):
        # در حالت ویرایش، فقط فیلدهای مشخص شده فقط خواندنی هستند
        # فیلد image برای تغییر تصویر در دسترس خواهد بود
        return self.readonly_fields

    def has_delete_permission(self, request, obj=None):
        return False  # جلوگیری از حذف تصاویر (اختیاری)
