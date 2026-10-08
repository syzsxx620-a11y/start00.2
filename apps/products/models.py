from decimal import Decimal

from django.db import models
from django.urls import reverse


class Currency(models.Model):
    """A display currency. `rate` is how many units of this currency equal 1 USD."""

    code = models.CharField(max_length=8, unique=True)
    name = models.CharField(max_length=50)
    symbol = models.CharField(max_length=8, default="$")
    rate = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        default=1,
        help_text="1 USD = how many units of this currency (e.g. EUR ~0.92, CNY ~7.2).",
    )
    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "currencies"
        ordering = ["code"]

    def __str__(self):
        return f"{self.code} ({self.symbol})"


class Category(models.Model):
    name = models.CharField(max_length=120)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to="categories/", blank=True, null=True)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name_plural = "categories"
        ordering = ["order", "name"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("products:list_by_category", args=[self.slug])


class Product(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    sku = models.CharField(max_length=64, unique=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="products",
    )
    price = models.DecimalField(max_digits=12, decimal_places=2, help_text="Price in USD.")
    compare_at_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Original price to show a strikethrough (USD).",
    )
    stock = models.PositiveIntegerField(default=0)
    short_description = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("products:detail", args=[self.slug])

    @property
    def main_image(self):
        img = self.images.first()
        return img.image if img else None

    @property
    def in_stock(self):
        return self.stock > 0

    def price_in(self, currency):
        """Convert the USD price into the given currency."""
        if currency is None:
            return self.price
        return (self.price * currency.rate).quantize(Decimal("0.01"))


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="products/")
    alt = models.CharField(max_length=200, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"{self.product.name} #{self.order}"
