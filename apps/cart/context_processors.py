from .models import Cart


def cart_count(request):
    """Expose the number of items in the visitor's cart to all templates."""
    count = 0
    session_key = request.session.session_key
    if session_key:
        try:
            count = Cart.objects.get(session_key=session_key).total_items
        except Cart.DoesNotExist:
            count = 0
    return {"cart_count": count}
