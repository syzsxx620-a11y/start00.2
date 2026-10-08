from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from apps.products.models import Product

from .models import Cart, CartItem


def _get_cart(request):
    """Return the cart for the current session, creating the session if needed."""
    if not request.session.session_key:
        request.session.create()
    cart, _ = Cart.objects.get_or_create(session_key=request.session.session_key)
    return cart


def cart_add(request, product_id):
    product = get_object_or_404(Product, pk=product_id, is_active=True)
    cart = _get_cart(request)
    try:
        quantity = int(request.POST.get("quantity", 1))
    except (TypeError, ValueError):
        quantity = 1
    quantity = max(1, min(quantity, product.stock or 1))

    item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    item.quantity = (item.quantity + quantity) if not created else quantity
    # Cap quantity at available stock.
    if product.stock and item.quantity > product.stock:
        item.quantity = product.stock
    item.save()

    messages.success(request, f"Added “{product.name}” to your cart.")
    return redirect("cart:detail")


def cart_detail(request):
    cart = _get_cart(request)
    items = cart.items.select_related("product").all()
    context = {"cart": cart, "items": items}
    return render(request, "cart/detail.html", context)


def cart_update(request):
    cart = _get_cart(request)
    if request.method == "POST":
        for item in cart.items.all():
            key = f"quantity_{item.id}"
            if key in request.POST:
                try:
                    quantity = int(request.POST[key])
                except (TypeError, ValueError):
                    quantity = item.quantity
                quantity = max(0, min(quantity, item.product.stock or quantity))
                if quantity == 0:
                    item.delete()
                else:
                    item.quantity = quantity
                    item.save()
    return redirect("cart:detail")


def cart_remove(request, item_id):
    cart = _get_cart(request)
    item = get_object_or_404(CartItem, pk=item_id, cart=cart)
    item.delete()
    messages.info(request, "Item removed from your cart.")
    return redirect("cart:detail")
