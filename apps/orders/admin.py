from django.contrib import admin

from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("product_name", "sku", "unit_price", "quantity")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "order_number",
        "full_name",
        "email",
        "country",
        "total",
        "status",
        "created_at",
    )
    list_filter = ("status", "country")
    search_fields = ("order_number", "full_name", "email", "phone", "company")
    readonly_fields = (
        "order_number",
        "subtotal",
        "shipping_fee",
        "total",
        "created_at",
    )
    fieldsets = (
        ("Order", {"fields": ("order_number", "status", "created_at")}),
        (
            "Customer",
            {
                "fields": (
                    "full_name",
                    "email",
                    "phone",
                    "company",
                    "country",
                    "address",
                    "city",
                    "state",
                    "postal_code",
                )
            },
        ),
        (
            "Totals (USD)",
            {"fields": ("subtotal", "shipping_fee", "total")},
        ),
        ("Notes", {"fields": ("notes",)}),
    )
    inlines = [OrderItemInline]
    actions = ["mark_shipped", "mark_delivered"]

    @admin.action(description="Mark selected orders as shipped")
    def mark_shipped(self, request, queryset):
        queryset.update(status="shipped")

    @admin.action(description="Mark selected orders as delivered")
    def mark_delivered(self, request, queryset):
        queryset.update(status="delivered")
