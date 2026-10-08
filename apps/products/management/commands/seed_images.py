"""Generate placeholder product images and attach them to products.

Run with:  python manage.py seed_images
"""
import os
from io import BytesIO

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from PIL import Image, ImageDraw, ImageFont

from apps.products.models import Product, ProductImage

WIDTH = HEIGHT = 640

CATEGORY_COLORS = {
    "electronics": (44, 96, 150),
    "home-garden": (185, 96, 60),
    "fashion-apparel": (134, 74, 132),
    "sports-outdoors": (43, 122, 86),
    "beauty-health": (178, 82, 106),
}
DEFAULT_COLOR = (15, 118, 110)

FONT_CANDIDATES = [
    "C:/Windows/Fonts/arialbd.ttf",
    "C:/Windows/Fonts/arial.ttf",
    "C:/Windows/Fonts/segoeui.ttf",
]


def _font(size):
    for path in FONT_CANDIDATES:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def _wrap(draw, text, font, max_width):
    words = text.split()
    lines = []
    line = ""
    for word in words:
        candidate = f"{line} {word}".strip()
        if draw.textlength(candidate, font=font) <= max_width:
            line = candidate
        else:
            if line:
                lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines


def _color_for(product):
    if product.category:
        return CATEGORY_COLORS.get(product.category.slug, DEFAULT_COLOR)
    return DEFAULT_COLOR


def _make_image(product):
    color = _color_for(product)
    img = Image.new("RGB", (WIDTH, HEIGHT))
    draw = ImageDraw.Draw(img)

    # vertical gradient from brand color to a darker shade
    bottom = tuple(int(c * 0.62) for c in color)
    for y in range(HEIGHT):
        t = y / (HEIGHT - 1)
        line = tuple(int(color[i] + (bottom[i] - color[i]) * t) for i in range(3))
        draw.line([(0, y), (WIDTH, y)], fill=line)

    # category label at the top
    label = (product.category.name if product.category else "ExportMall").upper()
    draw.text((40, 34), label, fill=(224, 232, 240), font=_font(26))

    # product name, wrapped and centered
    name_font = _font(46)
    lines = _wrap(draw, product.name, name_font, WIDTH - 100)
    line_height = 60
    y = (HEIGHT - len(lines) * line_height) // 2
    for text_line in lines:
        w = draw.textlength(text_line, font=name_font)
        draw.text(((WIDTH - w) // 2, y), text_line, fill=(255, 255, 255), font=name_font)
        y += line_height

    # SKU footer
    draw.text((40, HEIGHT - 60), f"SKU {product.sku}", fill=(224, 232, 240), font=_font(20))

    buf = BytesIO()
    img.save(buf, format="PNG")
    ProductImage.objects.create(
        product=product,
        image=ContentFile(buf.getvalue(), name=f"{product.slug}.png"),
        alt=product.name,
        order=0,
    )


class Command(BaseCommand):
    help = "Generate placeholder images for products that have none."

    def handle(self, *args, **options):
        created = 0
        for product in Product.objects.all():
            if product.images.exists():
                continue
            _make_image(product)
            created += 1
        self.stdout.write(self.style.SUCCESS(f"Generated {created} product image(s)."))
