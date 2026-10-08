from decimal import Decimal

from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def money(context, amount):
    """Format a USD amount in the visitor's currently selected currency."""
    try:
        amount = Decimal(str(amount))
    except (ValueError, TypeError, ArithmeticError):
        amount = Decimal("0")

    currency = context.get("current_currency")
    if currency is None:
        code, symbol, rate = "USD", "$", Decimal("1")
    else:
        code = currency.code
        symbol = currency.symbol
        rate = currency.rate or Decimal("1")

    converted = (amount * rate).quantize(Decimal("0.01"))
    return f"{symbol}{converted:,.2f} {code}"
