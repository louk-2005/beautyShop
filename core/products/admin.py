# django files
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Count
from django.contrib import messages


from mptt.admin import DraggableMPTTAdmin

# your files
from .models import Category, Product, ProductImages,ProductMessage


# ----------------------------------------------------------------------
# Inline for Product Images (Gallery)
# ----------------------------------------------------------------------
class ProductImagesInline(admin.TabularInline):
    model = ProductImages
    extra = 2
    fields = ('image', 'caption', 'image_preview')
    readonly_fields = ('image_preview',)

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 100px; height: 70px; object-fit: cover; border-radius: 4px;" />',
                obj.image.url
            )
        return "بدون تصویر"

    image_preview.short_description = "پیش‌نمایش"


# ----------------------------------------------------------------------
# Category Admin
# ----------------------------------------------------------------------
@admin.register(Category)
class CategoryAdmin(DraggableMPTTAdmin):
    # حذف created_at چون در مدل وجود ندارد
    list_display = ('tree_actions', 'indented_title','name', 'parent', 'image_thumbnail', 'product_count')
    list_display_links = ('indented_title',)
    list_filter = ('parent',)
    search_fields = ('name',)
    readonly_fields = ('image_preview',)
    list_per_page = 20

    fieldsets = (
        (None, {
            'fields': ('name', 'parent')
        }),
        ('تصویر', {
            'fields': ('image', 'image_preview'),
            'classes': ('collapse',)
        }),
    )

    def image_thumbnail(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 100px; height: 100px; object-fit: cover; border-radius: 5px;" />',
                obj.image.url
            )
        return "-"

    image_thumbnail.short_description = "تصویر"

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<div><img src="{}" style="max-width: 400px; max-height: 400px; border-radius: 8px;" /></div>',
                obj.image.url
            )
        return "تصویری بارگذاری نشده"

    image_preview.short_description = "پیش‌نمایش تصویر"

    def product_count(self, obj):
        count = getattr(obj, 'products_count', None)
        if count is None:
            count = obj.products.count()
        return format_html(
            '<span style="color: #417690; font-weight: bold;">{} محصول</span>',
            count
        )

    product_count.short_description = "تعداد محصولات"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(products_count=Count('products')).select_related('parent')


# ----------------------------------------------------------------------
# Product Admin
# ----------------------------------------------------------------------
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'category',
        'image_thumbnail',
        'price_display',
        "avg_rating_display",
        'stock_status',
        'gallery_count',
        'created_at'
    )
    list_filter = ('category', 'created_at')
    search_fields = ('name', 'description', 'category__name')
    list_per_page = 20
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)

    readonly_fields = ('created_at', 'main_image_preview', 'stock_status')
    inlines = [ProductImagesInline]

    actions = ['reset_stock', 'duplicate_product']

    fieldsets = (
        ('اطلاعات اصلی', {
            'fields': ('name', 'category', 'description')
        }),
        ('قیمت و موجودی', {
            'fields': ('first_price','price', 'stock', 'stock_status'),
        }),
        ('تصویر اصلی', {
            'fields': ('image', 'main_image_preview'),
        }),
        ('محتوای کامل', {
            'fields': ('content',),
            'classes': ('collapse',),
        }),
        ('تاریخ‌ها', {
            'fields': ('created_at',),
            'classes': ('collapse',),
        }),
    )

    # --- متدهای نمایش ---
    def price_display(self, obj):
        if obj.first_price and obj.first_price > obj.price:
            discount = int((1 - obj.price / obj.first_price) * 100)
            return format_html(
                '<span style="text-decoration: line-through; color: #999; font-size: 0.85em;">{}</span> <span style="color: green; font-weight: bold;">{}</span> <span style="background: red; color: white; padding: 2px 5px; border-radius: 4px; font-size: 0.8em;">{}%</span>',
                f"{obj.first_price:,.0f}", f"{obj.price:,.0f} ", discount
            )
        return f"{obj.price:,.0f} تومان"
    def avg_rating_display(self, obj):
        avg = obj.average_rating or 0
        print(avg)
        full_star = '<span style="color: gold;">★</span>'
        empty_star = '<span style="color: #ccc;">★</span>'
        stars = full_star * int(avg) + empty_star * (5 - int(avg))
        return format_html(
            stars,
            round(avg, 1))
    def image_thumbnail(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 100px; height: 100px; object-fit: cover; border-radius: 5px;" />',
                obj.image.url
            )
        return "-"

    image_thumbnail.short_description = "تصویر"

    def main_image_preview(self, obj):
        if obj.image:
            return format_html(
                '<div><img src="{}" style="max-width: 400px; max-height: 400px; border-radius: 8px;" /></div>',
                obj.image.url
            )
        return "تصویری بارگذاری نشده"

    main_image_preview.short_description = "پیش‌نمایش تصویر اصلی"



    price_display.short_description = "قیمت"
    price_display.admin_order_field = 'price'

    def stock_status(self, obj):
        if obj.stock > 10:
            color = 'green'
            text = f"موجود ({obj.stock})"
        elif obj.stock > 0:
            color = 'orange'
            text = f"کم ({obj.stock})"
        else:
            color = 'red'
            text = "ناموجود"

        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, text
        )

    stock_status.short_description = "وضعیت موجودی"
    stock_status.admin_order_field = 'stock'

    def gallery_count(self, obj):
        count = obj.images.count()
        # اصلاح شده: products به جای shop
        return format_html(
            '<a href="{}?product__id={}">{} تصویر</a>',
            reverse('admin:products_productimages_changelist'), obj.id, count
        ) if count > 0 else "بدون گالری"

    gallery_count.short_description = "گالری"

    # --- اکشن‌ها ---

    @admin.action(description='صفر کردن موجودی محصولات انتخاب شده')
    def reset_stock(self, request, queryset):
        updated = queryset.update(stock=0)
        self.message_user(request, f'موجودی {updated} محصول به صفر تغییر یافت.', messages.WARNING)

    @admin.action(description='کپی محصولات انتخاب شده')
    def duplicate_product(self, request, queryset):
        # نکته: برای کپی صحیح رابطه‌ها (مانند تصاویر) باید کمی کد بیشتر نوشت،
        # اما برای فیلدهای ساده این کد کار می‌کند.
        clones_count = 0
        for product in queryset:
            product.pk = None
            product.name = f"{product.name} (کپی)"
            product.stock = 0
            product.save()
            clones_count += 1
        self.message_user(request, f'{clones_count} محصول با موفقیت کپی شد.', messages.SUCCESS)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('category').prefetch_related('images')


# ----------------------------------------------------------------------
# Product Images Admin
# ----------------------------------------------------------------------
@admin.register(ProductImages)
class ProductImagesAdmin(admin.ModelAdmin):
    # حذف created_at چون در مدل وجود ندارد
    list_display = ('image_thumbnail', 'caption', 'product_link')
    list_filter = ('product',)
    search_fields = ('caption', 'product__name')
    readonly_fields = ('main_image_preview',)

    def image_thumbnail(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 100px; height: 100px; object-fit: cover; border-radius: 5px;" />',
                obj.image.url
            )
        return "-"

    image_thumbnail.short_description = "تصویر"

    def main_image_preview(self, obj):
        if obj.image:
            return format_html(
                '<div><img src="{}" style="width: 400px; height: 400px; border-radius: 8px;" /></div>',
                obj.image.url
            )
        return "تصویری بارگذاری نشده"
    main_image_preview.short_description = "پیش‌نمایش تصویر اصلی"

    def product_link(self, obj):
        # اصلاح شده: products به جای shop
        url = reverse("admin:products_product_change", args=[obj.product.id])
        return format_html('<a href="{}">{}</a>', url, obj.product.name)

    product_link.short_description = "محصول"

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('product')



class ProductMessageAdmin(DraggableMPTTAdmin):
    list_display = ('tree_actions', 'indented_title','name','email','is_shown',)
    list_display_links = ('indented_title',)
admin.site.register(ProductMessage, ProductMessageAdmin)

