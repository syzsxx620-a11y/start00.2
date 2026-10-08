from decimal import Decimal

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render

from apps.cart.models import Cart
from apps.cart.views import _get_cart

from .forms import CheckoutForm
from .models import Order, OrderItem, generate_order_number


def _shipping_fee(subtotal):
    """Flat international shipping, free above a threshold."""
    threshold = Decimal(settings.FREE_SHIPPING_THRESHOLD_USD)
    if subtotal >= threshold:
        return Decimal("0.00")
    return Decimal(settings.SHIPPING_FLAT_RATE_USD)


def checkout(request):
    cart = _get_cart(request)
    items = cart.items.select_related("product").all()
    if not items:
        messages.info(request, "Your cart is empty.")
        return redirect("cart:detail")

    form = CheckoutForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        with transaction.atomic():
            # Re-check stock inside the transaction and build line snapshots.
            order_items = []
            subtotal = Decimal("0.00")
            for item in items:
                product = item.product
                if item.quantity > product.stock:
                    messages.error(
                        request,
                        f"Not enough stock for “{product.name}” "
                        f"(available: {product.stock}).",
                    )
                    return redirect("cart:detail")
                product.stock -= item.quantity
                product.save(update_fields=["stock"])
                line_total = product.price * item.quantity
                subtotal += line_total
                order_items.append(
                    OrderItem(
                        product=product,
                        product_name=product.name,
                        sku=product.sku,
                        unit_price=product.price,
                        quantity=item.quantity,
                    )
                )

            shipping = _shipping_fee(subtotal)
            order = Order.objects.create(
                order_number=generate_order_number(),
                user=request.user if request.user.is_authenticated else None,
                full_name=form.cleaned_data["full_name"],
                email=form.cleaned_data["email"],
                phone=form.cleaned_data["phone"],
                company=form.cleaned_data["company"],
                country=form.cleaned_data["country"],
                address=form.cleaned_data["address"],
                city=form.cleaned_data["city"],
                state=form.cleaned_data["state"],
                postal_code=form.cleaned_data["postal_code"],
                notes=form.cleaned_data["notes"],
                subtotal=subtotal,
                shipping_fee=shipping,
                total=subtotal + shipping,
            )
            for oi in order_items:
                oi.order = order
            OrderItem.objects.bulk_create(order_items)

        # Clear the cart after a successful order.
        cart.items.all().delete()
        request.session["last_order_number"] = order.order_number
        return redirect("orders:confirmation", order_number=order.order_number)

    shipping_fee = _shipping_fee(cart.subtotal)
    context = {
        "form": form,
        "cart": cart,
        "items": items,
        "subtotal": cart.subtotal,
        "shipping_fee": shipping_fee,
        "total": cart.subtotal + shipping_fee,
    }
    return render(request, "orders/checkout.html", context)


def confirmation(request, order_number):
    order = get_object_or_404(Order, order_number=order_number)
    return render(request, "orders/confirmation.html", {"order": order})


def order_track(request):
    order = None
    error = None
    if request.method == "POST":
        number = request.POST.get("order_number", "").strip()
        email = request.POST.get("email", "").strip()
        order = (
            Order.objects.filter(order_number=number, email__iexact=email).first()
            if number and email
            else None
        )
        if order is None:
            error = "No order found matching that order number and email."
    return render(request, "orders/track.html", {"order": order, "error": error})


def order_detail(request, order_number, email):
    order = get_object_or_404(Order, order_number=order_number, email__iexact=email)
    return render(request, "orders/detail.html", {"order": order})


@login_required
def order_history(request):
    orders = request.user.orders.all()
    return render(request, "orders/history.html", {"orders": orders})
