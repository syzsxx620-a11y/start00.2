from django.contrib import admin

from .models import Category, Currency, Product, ProductImage


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "symbol", "rate", "is_default", "is_active")
    list_editable = ("rate", "is_default", "is_active")


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "order", "is_active")
    list_editable = ("order", "is_active")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "sku",
        "category",
        "price",
        "stock",
        "is_featured",
        "is_active",
    )
    list_filter = ("category", "is_featured", "is_active")
    list_editable = ("price", "stock", "is_featured", "is_active")
    search_fields = ("name", "sku", "short_description")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [ProductImageInline]
