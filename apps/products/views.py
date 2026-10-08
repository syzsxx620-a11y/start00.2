from django.db.models import Q
from django.shortcuts import get_object_or_404, render

from .models import Category, Product


def product_list(request, category_slug=None):
    products = Product.objects.filter(is_active=True).select_related("category")
    category = None

    if category_slug:
        category = get_object_or_404(Category, slug=category_slug, is_active=True)
        products = products.filter(category=category)

    q = request.GET.get("q", "").strip()
    if q:
        products = products.filter(
            Q(name__icontains=q)
            | Q(sku__icontains=q)
            | Q(short_description__icontains=q)
            | Q(description__icontains=q)
        )

    sort = request.GET.get("sort", "")
    if sort == "price_asc":
        products = products.order_by("price")
    elif sort == "price_desc":
        products = products.order_by("-price")
    elif sort == "name":
        products = products.order_by("name")
    else:
        products = products.order_by("-created_at")

    context = {
        "products": products,
        "category": category,
        "categories": Category.objects.filter(is_active=True),
        "q": q,
        "sort": sort,
    }
    return render(request, "products/list.html", context)


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    related = (
        Product.objects.filter(is_active=True, category=product.category)
        .exclude(pk=product.pk)[:4]
    )
    context = {
        "product": product,
        "images": product.images.all(),
        "related": related,
    }
    return render(request, "products/detail.html", context)
