"""Seed the database with demo currencies, categories and products.

Run with:  python manage.py seed_demo
"""
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils.text import slugify

from apps.products.models import Category, Currency, Product


class Command(BaseCommand):
    help = "Seed demo data (currencies, categories, products) for the storefront."

    def handle(self, *args, **options):
        self._seed_currencies()
        categories = self._seed_categories()
        self._seed_products(categories)
        self.stdout.write(self.style.SUCCESS("Demo data seeded successfully."))

    def _seed_currencies(self):
        currencies = [
            ("USD", "US Dollar", "$", "1.0000", True),
            ("EUR", "Euro", "€", "0.9200", False),
            ("CNY", "Chinese Yuan", "¥", "7.2000", False),
            ("GBP", "British Pound", "£", "0.7900", False),
        ]
        # Ensure only one default.
        Currency.objects.filter(is_default=True).update(is_default=False)
        for code, name, symbol, rate, is_default in currencies:
            obj, created = Currency.objects.get_or_create(
                code=code,
                defaults={
                    "name": name,
                    "symbol": symbol,
                    "rate": Decimal(rate),
                    "is_default": is_default,
                    "is_active": True,
                },
            )
            if not created and is_default:
                obj.is_default = True
                obj.save(update_fields=["is_default"])

    def _seed_categories(self):
        data = [
            ("Electronics", "Consumer electronics and gadgets."),
            ("Home & Garden", "Home decor, kitchen and garden supplies."),
            ("Fashion & Apparel", "Clothing, bags and accessories."),
            ("Sports & Outdoors", "Fitness, camping and outdoor gear."),
            ("Beauty & Health", "Skincare, beauty and wellness products."),
        ]
        categories = {}
        for idx, (name, desc) in enumerate(data):
            category, _ = Category.objects.get_or_create(
                slug=slugify(name),
                defaults={"name": name, "description": desc, "order": idx},
            )
            categories[name] = category
        return categories

    def _seed_products(self, categories):
        products = [
            # name, category, price, compare_at, stock, short, featured
            ("Wireless Bluetooth Headphones", "Electronics", "59.90", "79.90", 120, "Noise-cancelling over-ear headphones with 30h battery life.", True),
            ("Smart Fitness Watch", "Electronics", "89.00", None, 80, "Heart-rate, GPS and sleep tracking in a sleek design.", True),
            ("Portable Power Bank 20000mAh", "Electronics", "25.50", "35.00", 200, "Fast-charging power bank with dual USB-C ports.", False),
            ("Ceramic Dinnerware Set (16pcs)", "Home & Garden", "72.00", "95.00", 60, "Elegant 16-piece porcelain dinnerware set.", True),
            ("Stainless Steel Cookware Set", "Home & Garden", "128.00", None, 40, "12-piece stainless steel pots and pans.", False),
            ("LED Table Lamp", "Home & Garden", "18.90", "24.90", 150, "Dimmable LED desk lamp with USB charging.", False),
            ("Unisex Canvas Backpack", "Fashion & Apparel", "34.50", "45.00", 90, "Durable water-resistant canvas backpack, 25L.", True),
            ("Cotton T-Shirt (3-pack)", "Fashion & Apparel", "22.00", None, 300, "Soft 100% cotton crew-neck tees.", False),
            ("Insulated Water Bottle 1L", "Sports & Outdoors", "15.80", "19.90", 250, "Vacuum-insulated stainless steel bottle.", True),
            ("Yoga Mat with Carry Strap", "Sports & Outdoors", "21.00", None, 110, "Non-slip 6mm yoga mat with strap.", False),
            ("Vitamin C Serum 30ml", "Beauty & Health", "16.50", "22.00", 180, "Brightening facial serum with hyaluronic acid.", True),
            ("Electric Toothbrush", "Beauty & Health", "29.90", "39.90", 70, "Rechargeable sonic toothbrush with 4 modes.", False),
        ]

        for name, cat_name, price, compare_at, stock, short, featured in products:
            slug = slugify(name)
            defaults = {
                "sku": self._sku(slug),
                "category": categories[cat_name],
                "price": Decimal(price),
                "compare_at_price": Decimal(compare_at) if compare_at else None,
                "stock": stock,
                "short_description": short,
                "description": f"{short}\n\nQuality-tested for international export. "
                "Inquiries for bulk / wholesale pricing are welcome.",
                "is_featured": featured,
                "is_active": True,
            }
            Product.objects.get_or_create(slug=slug, defaults=defaults)

    def _sku(self, slug):
        base = "".join(part[:4] for part in slug.split("-") if part)[:12].upper()
        return f"SKU-{base}"
