from apps.products.models import Category, Currency


def currency(request):
    """Expose available currencies and the visitor's current selection."""
    currencies = list(Currency.objects.filter(is_active=True).order_by("code"))
    code = request.session.get("currency")
    current = next((c for c in currencies if c.code == code), None)
    if current is None:
        current = next((c for c in currencies if c.is_default), None)
    if current is None and currencies:
        current = currencies[0]
    return {
        "currencies": currencies,
        "current_currency": current,
    }


def categories(request):
    """Expose active product categories for the site navigation."""
    return {"nav_categories": Category.objects.filter(is_active=True)}
