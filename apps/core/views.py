from django.shortcuts import redirect, render

from apps.products.models import Category, Product


def home(request):
    featured = Product.objects.filter(is_active=True, is_featured=True)[:8]
    new_arrivals = Product.objects.filter(is_active=True).order_by("-created_at")[:8]
    categories = Category.objects.filter(is_active=True)
    context = {
        "featured": featured,
        "new_arrivals": new_arrivals,
        "categories": categories,
    }
    return render(request, "home.html", context)


def set_currency(request):
    """Store the visitor's preferred display currency in the session."""
    code = request.POST.get("currency") or request.GET.get("currency")
    next_url = request.POST.get("next") or request.GET.get("next") or "/"
    # Only allow internal redirects (avoid open redirect).
    if not next_url.startswith("/") or next_url.startswith("//"):
        next_url = "/"
    if code:
        request.session["currency"] = code
    return redirect(next_url)
