from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Sum, F
from django.contrib import messages

# your files
from .models import Cart, CartItem


# ----------------------------------------------------------------------
# Inline for Cart Items
# ----------------------------------------------------------------------
class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0  # عدم نمایش ردیف‌های اضافی خالی
    fields = ('product_link', 'quantity', 'item_total_price')
    readonly_fields = ('product_link', 'item_total_price')

    def item_total_price(self, obj):
        # محاسبه قیمت کل آیتم (تعداد * قیمت واحد)
        if obj.product and obj.product.price:
            price = obj.product.price * obj.quantity
            return format_html("<span style='direction: ltr; display: inline-block;'>{} تومان</span>", f"{price:,.0f}")
        return "-"

    item_total_price.short_description = "جمع کل"

    def product_link(self, obj):
        if obj.product:
            try:
                # لینک به صفحه ویرایش محصول در ادمین
                # توجه: مطمئن شوید که نام اپلیکیشن محصولات 'products' است
                url = reverse("admin:products_product_change", args=[obj.product.id])
                return format_html('<a href="{}" target="_blank">{}</a>', url, obj.product.name)
            except Exception:
                return obj.product.name
        return "-"

    product_link.short_description = "محصول"

    def has_add_permission(self, request, obj=None):
        return True


# ----------------------------------------------------------------------
# Cart Admin
# ----------------------------------------------------------------------
@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = (
        'id_display',
        'cart_token_display',
        'user_info',
        'items_count_display',
        'total_price_display',
        'created_at'
    )
    list_filter = ('created_at', 'user')
    # جستجو بر اساس توکن سبد، نام کاربر و آیدی
    search_fields = ('cart_token', 'user__phone_number', 'user__email', 'id')
    readonly_fields = (
    'created_at', 'updated_at', 'total_price_display', 'items_count_display', 'id_display', 'cart_token_display')
    inlines = [CartItemInline]
    date_hierarchy = 'created_at'

    fieldsets = (
        ('اطلاعات سبد', {
            'fields': ('id_display', 'cart_token_display', 'user', 'created_at', 'updated_at')
        }),
        ('خلاصه مالی', {
            'fields': ('items_count_display', 'total_price_display'),
            'description': 'این مقادیر به صورت خودکار محاسبه می‌شوند.'
        }),
    )

    # --- متدهای نمایش ---

    def id_display(self, obj):
        return str(obj.id)

    id_display.short_description = "شناسه (ID)"

    # متدی که باعث خطا می‌شد - اصلاح شده
    def cart_token_display(self, obj):
        # نمایش بخشی از توکن برای خوانایی بهتر
        token_str = str(obj.cart_token)
        return format_html("<code>{}</code>", token_str)

    cart_token_display.short_description = "توکن سبد"

    def user_info(self, obj):
        if obj.user:
            try:
                # پیدا کردن نام اپلیکیشن یوزر به صورت خودکار
                user_model = obj.user.__class__
                app_label = user_model._meta.app_label
                model_name = user_model._meta.model_name

                url = reverse(f"admin:{app_label}_{model_name}_change", args=[obj.user.id])
                # نمایش شماره تماس به عنوان لینک
                return format_html('<a href="{}">{}</a>', url, obj.user.phone_number)
            except Exception:
                return obj.user.phone_number
        else:
            # اگر کاربر لاگین نیست (مهمان)، نمایش توکن
            return format_html(
                "<span style='color:#777;'>{}</span>",
                "مهمان"
            )

    user_info.short_description = "کاربر"
    user_info.admin_order_field = 'user'

    def items_count_display(self, obj):
        count = obj.items.count()
        return format_html(
            '<span style="background: #417690; color: white; padding: 3px 10px; border-radius: 10px;">{} قلم</span>',
            count
        )

    items_count_display.short_description = "تعداد اقلام"

    def total_price_display(self, obj):
        # محاسبه جمع کل با استفاده از annotates برای بهینه‌سازی
        total = obj.items.annotate(
            item_total=F('quantity') * F('product__price')
        ).aggregate(sum_total=Sum('item_total'))['sum_total']

        if total:
            return format_html(
                '<b style="color: green; font-size: 1.2em; direction: ltr; display: inline-block;">{} تومان</b>',
                f"{total:,.0f}"
            )
        return "0 تومان"

    total_price_display.short_description = "جمع کل سبد"

    def get_queryset(self, request):
        # بهینه‌سازی کوئری برای جلوگیری از مشکل N+1
        return super().get_queryset(request).prefetch_related('items__product').select_related('user')


# ----------------------------------------------------------------------
# Cart Item Admin (Standalone)
# ----------------------------------------------------------------------
@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart_link', 'product', 'quantity', 'item_total_display', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('product__name', 'cart__cart_token')
    readonly_fields = ('item_total_display', 'created_at')

    def item_total_display(self, obj):
        if obj.product:
            price = obj.product.price * obj.quantity
            return f"{price:,.0f} تومان"
        return "-"

    item_total_display.short_description = "جمع قیمت"

    def cart_link(self, obj):
        try:
            url = reverse("admin:cart_cart_change", args=[obj.cart.id])
            return format_html('<a href="{}">سبد {}</a>', url, str(obj.cart.cart_token)[:8])
        except Exception:
            return str(obj.cart.cart_token)

    cart_link.short_description = "سبد خرید"

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('product', 'cart')