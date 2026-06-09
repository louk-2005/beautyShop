from django.contrib import admin
from django.utils.html import format_html, escape
from django.urls import reverse
from django.contrib import messages
from django.utils.translation import ngettext
from django.utils.safestring import mark_safe

from .models import Order, OrderItem


# ---------------------------------------------------------
# Inline برای نمایش آیتم‌های داخل سفارش
# ---------------------------------------------------------
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'quantity', 'price', 'total_item_price')
    fields = ('product', 'quantity', 'price', 'total_item_price')

    def total_item_price(self, obj):
        if obj.price:
            return f"{obj.quantity * obj.price:,} تومان"
        return "-"

    total_item_price.short_description = "جمع کل"


# ---------------------------------------------------------
# ادمین اصلی سفارشات
# ---------------------------------------------------------
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'full_name',
        'phone_number',
        'total_price_display',
        'status_colored',
        'items_preview',
        'created_at'
    )

    list_display_links = ('id', 'full_name')

    list_filter = ('status', 'created_at')

    search_fields = ('id', 'user__phone_number', 'full_name', 'phone_number', 'postal_code', 'payment_ref_id')

    # فیلدهای فقط خواندنی (شامل فیلدهای جدید پرداخت)
    readonly_fields = (
        'total_price',
        'created_at',
        'display_items_detail',
        'payment_authority',
        'payment_ref_id',
        'paid_at'
    )

    date_hierarchy = 'created_at'

    inlines = [OrderItemInline]

    actions = ['mark_as_paid', 'mark_as_shipped', 'mark_as_delivered', 'mark_as_canceled']

    fieldsets = (
        ('اطلاعات مشتری', {
            'fields': ('user', 'full_name', 'phone_number')
        }),
        ('آدرس ارسال', {
            'fields': ('province', 'city', 'postal_code', 'address')
        }),
        ('اطلاعات مالی', {
            'fields': ('total_price', 'display_items_detail')
        }),
        ('وضعیت سفارش', {
            'fields': ('status',)
        }),
        ('اطلاعات پرداخت', {
            'classes': ('collapse',),  # این بخش به صورت پیش‌فرض جمع می‌شود
            'fields': ('payment_authority', 'payment_ref_id', 'paid_at'),
            'description': 'اطلاعات بازگشتی از درگاه پرداخت'
        }),
    )

    # -----------------------------------------------------
    # مدیریت ذخیره سازی
    # -----------------------------------------------------
    def save_model(self, request, obj, form, change):
        if not change and not obj.user_id:
            obj.user = request.user
        super().save_model(request, obj, form, change)

    # -----------------------------------------------------
    # متدهای کمکی نمایش
    # -----------------------------------------------------

    def total_price_display(self, obj):
        return f"{obj.total_price:,} تومان"

    total_price_display.short_description = "مبلغ کل"
    total_price_display.admin_order_field = 'total_price'

    def status_colored(self, obj):
        colors = {
            'pending': '#6c757d',
            'paid': '#0d6efd',
            'shipped': '#fd7e14',
            'delivered': '#198754',
            'canceled': '#dc3545'
        }
        color = colors.get(obj.status, 'black')
        return format_html(
            '<b style="color:{}; padding:3px 10px; border-radius:5px; background-color:{}20;">{}</b>',
            color,
            color,
            obj.get_status_display()
        )

    status_colored.short_description = "وضعیت"
    status_colored.admin_order_field = 'status'

    def items_preview(self, obj):
        items = obj.items.all()[:3]
        if not items:
            return "-"

        html = "<ul style='margin:0; padding-right:15px; text-align:right;'>"
        for item in items:
            html += f"<li>{escape(item.product.name)} ({item.quantity})</li>"

        count = obj.items.count()
        if count > 3:
            html += f"<li><i>+{count - 3} محصول دیگر...</i></li>"

        html += "</ul>"
        return mark_safe(html)

    items_preview.short_description = "محصولات خریداری شده"

    def display_items_detail(self, obj):
        items = obj.items.all()
        if not items:
            return "موردی وجود ندارد"

        html = "<table style='width:100%; border-collapse: collapse;'>"
        html += "<tr style='border-bottom:1px solid #ddd;'><th style='text-align:right; padding:5px;'>محصول</th><th style='text-align:center;'>تعداد</th><th style='text-align:left;'>قیمت واحد</th></tr>"
        for item in items:
            html += f"<tr style='border-bottom:1px solid #eee;'>"
            html += f"<td style='padding:5px;'>{escape(item.product.name)}</td>"
            html += f"<td style='text-align:center;'>{item.quantity}</td>"
            html += f"<td style='text-align:left;'>{item.price:,} تومان</td>"
            html += f"</tr>"
        html += "</table>"
        return mark_safe(html)

    display_items_detail.short_description = "جزئیات محصولات سفارش داده شده"

    # -----------------------------------------------------
    # اکشن‌ها
    # -----------------------------------------------------

    def mark_as_paid(self, request, queryset):
        updated = queryset.update(status='paid')
        self.message_user(request, ngettext(
            '%d سفارش به وضعیت "پرداخت شده" تغییر یافت.',
            '%d سفارش به وضعیت "پرداخت شده" تغییر یافتند.',
            updated,
        ) % updated, messages.SUCCESS)

    mark_as_paid.short_description = "تغییر وضعیت به: پرداخت شده"

    def mark_as_shipped(self, request, queryset):
        updated = queryset.update(status='shipped')
        self.message_user(request, f'{updated} سفارش به "در حال ارسال" تغییر یافت.', messages.SUCCESS)

    mark_as_shipped.short_description = "تغییر وضعیت به: در حال ارسال"

    def mark_as_delivered(self, request, queryset):
        updated = queryset.update(status='delivered')
        self.message_user(request, f'{updated} سفارش به "تحویل داده شده" تغییر یافت.', messages.SUCCESS)

    mark_as_delivered.short_description = "تغییر وضعیت به: تحویل داده شده"

    def mark_as_canceled(self, request, queryset):
        updated = queryset.update(status='canceled')
        self.message_user(request, f'{updated} سفارش لغو گردید.', messages.WARNING)

    mark_as_canceled.short_description = "لغو سفارشات انتخاب شده"


# ---------------------------------------------------------
# ادمین آیتم‌های سفارش
# ---------------------------------------------------------
@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'order_link', 'product', 'quantity', 'price_display', 'total_display', 'order_status')
    list_filter = ('order__status', 'product')
    search_fields = ('order__id', 'product__name', 'order__full_name')

    readonly_fields = ('price',)
    ordering = ('-id',)

    def order_link(self, obj):
        url = reverse("admin:orders_order_change", args=[obj.order.id])
        return format_html('<a href="{}">سفارش #{}</a>', url, obj.order.id)

    order_link.short_description = "سفارش"
    order_link.admin_order_field = 'order__id'

    def price_display(self, obj):
        return f"{obj.price:,} تومان"

    price_display.short_description = "قیمت واحد"

    def total_display(self, obj):
        total = obj.quantity * obj.price
        return format_html('<b style="color:#0d6efd;">{} تومان</b>', f"{total:,}")

    total_display.short_description = "جمع کل"

    def order_status(self, obj):
        colors = {
            'pending': '#6c757d', 'paid': '#0d6efd', 'shipped': '#fd7e14',
            'delivered': '#198754', 'canceled': '#dc3545'
        }
        color = colors.get(obj.order.status, 'black')
        return format_html('<span style="color:{};">{}</span>', color, obj.order.get_status_display())

    order_status.short_description = "وضعیت سفارش"